"""
    Convenience functions for authentication.

    The logical flow for a visitor is to;

    #.  Obtain a session (:py:func:`current_session`)

    #.  Hit a resource that requires a login (a :py:func:`flask.Flask.route`
        decorated with :py:func:`login_required`)

    #.  Start the login sequence (:py:func:`login_sequence_start`). This is
        the "entry" event.

    #.  Submit a set of credentials (:py:func:`login_sequence_retrieve` is
        used to associate the submission with the previously created
        sequence);

        *   no second factor configured calls
            :py:func:`login_sequence_complete`,

        *   a second factor configured calls
            :py:func:`login_sequence_continue`.
"""

import datetime

from functools import wraps

from flask import abort
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for

# pylint: disable=no-name-in-module
# pylint: disable=import-error
from flask.ext.babel import get_locale as get_babel_locale
from flask.ext.babel import get_timezone as get_babel_timezone


def current_session():
    """
        Return the current session as recorded in the database, or record
        the current session in the database.

        :returns:   A :py:class:`piko.db.model.Session` object.
    """
    from piko.db import db
    from piko.db.model import Session

    _session = db.session.query(Session).filter_by(
        uuid=session.get('uuid', None)
    ).first()

    if _session is None:
        _session = Session()
        db.session.add(_session)
        db.session.commit()

    session['uuid'] = _session.uuid

    return _session


# pylint: disable=invalid-name
def login_required(f):
    """
        Decorator function for route controllers that require a login.
    """
    @wraps(f)
    # pylint: disable=missing-docstring
    def decorated_function(*args, **kwargs):
        person_id = g.get('user', None)

        if person_id is None:
            person_id = session.get('person_id', None)

        if person_id is None:
            return redirect(url_for('piko.login', next=request.url))

        from piko.db import db
        from piko.db.model import Person
        person = db.session.query(Person).filter_by(uuid=person_id).first()

        if person is None:
            return redirect(url_for('piko.login', next=request.url))

        g.user = person.uuid

        return f(*args, **kwargs)

    return decorated_function


def login_sequence_account_get_or_create(type_name, remote_id, name):
    """
        Obtains the existing or creates a new account.

        Returns a :py:func:`werkzeug.utils.redirect`, imported as
        ``from flask import redirect``, for accounts with a second
        factor configured, or passes responsibilities on to
        :py:func:`piko.app.authn.login_sequence_complete`.

        :param  type_name:  The account type name.
        :type   type_name:  str
        :param  remote_id:  The remote ID for the account.
        :type   remote_id:  str
        :param  name:       The account (display) name.
        :type   name:       str
    """

    from piko.db import db
    from piko.db.model import Account

    account = db.session.query(Account).filter_by(
        remote_id=remote_id,
        type_name=type_name
    ).first()

    if account is None:
        account = Account(
            name=name,
            remote_id=remote_id,
            type_name=type_name,
            locale=get_babel_locale().__str__(),
            timezone=get_babel_timezone().__str__()
        )

        db.session.add(account)
        db.session.commit()

        account = db.session.query(Account).filter_by(
            remote_id=remote_id,
            type_name=type_name
        ).first()

    else:
        account.name = name

        if len(account.second_factors) > 0:
            session['_flashes'] = []

            login_sequence_associate_account(account.uuid)

            # pylint: disable=unused-variable
            transaction, uuid = login_sequence_continue()

            return redirect(url_for('piko.login_otp'))

    _session = current_session()

    _session.account_id = account.uuid
    session['account_id'] = account.uuid

    return login_sequence_complete(True)


def login_sequence_associate_account(uuid):
    """
        Associate an :py:attr:`piko.db.model.Account.uuid` with the
        current :py:attr:`piko.db.model.Session`, without disclosing
        the validity of the account to the visitor via, for example, a
        cookie value.

        This is used for staged account login processing -- we keep the
        information about a user having attempted to login with an
        otherwise valid account on the server.
    """
    _session = current_session()
    _session.associate_account_id(uuid)


def login_sequence_associate_person(uuid):
    """
        Associate an :py:attr:`piko.db.model.Account.uuid` with the
        current :py:attr:`piko.db.model.Session`, without disclosing
        the validity of the account to the visitor via, for example, a
        cookie value.

        This is used for staged account login processing -- we keep the
        information about a user having attempted to login with an
        otherwise valid account on the server.
    """
    _session = current_session()
    _session.associate_person_id(uuid)


def login_sequence_complete(success):
    """
        Complete a login sequence -- successfully or not -- and
        obsolete the associated list of
        :py:class:`piko.db.model.SessionTransaction` objects.

        Create the audit log entry.

        Return the appropriate redirect.

        :param  success:    Mark this login sequence as completed
                            successfully, or not.
        :type   success:    bool

        :returns:           :py:func:`werkzeug.utils.redirect`
    """
    from piko.db import db
    from piko.db.model import AccountLogin

    _session = current_session()

    # Reset all ongoing transactions regardless of success or failure.
    _session.reset_transactions()

    # Store the current redirect.
    _redirect = _session.redirect

    # Zero out the stored redirect.
    _session.redirect = None

    # Store the record on the login attempt.
    db.session.add(
        AccountLogin(
            account_id=_session.account_id,
            person_id=_session.person_id,
            success=success
        )
    )

    if not success:
        db.session.delete(_session)
        db.session.commit()
        session.clear()
        _redirect = url_for('piko.login')

    db.session.commit()

    session['account_id'] = _session.account_id
    session['person_id'] = _session.person_id

    return redirect(_redirect)


def login_sequence_continue():
    """
        Mark the session with a second transaction, such as for a TOTP/HOTP/TAN
        sequence.

        Returns the transaction to associate the validation of the current
        credentials to, which can be an asynchronous :py:class:`celery.Celery`
        task, for which we store the task ID as part of the transaction.

        Also returns the uuid for the new form.

        :returns:   A tuple of the :py:class:`piko.db.model.SessionTransaction`
                    object for the entry event, and the :py:class:`uuid.UUID`.
    """

    from piko.db import db
    from piko.db.model import SessionTransaction

    _session = current_session()

    if not _session.account_id and not _session.person_id:
        return (None, abort(500))

    if len(_session.transactions) == 2:
        return (
            _session.transactions[0],
            _session.transactions[1].transaction_id
        )

    _session.transactions.append(SessionTransaction())

    db.session.commit()

    return _session.transactions[0], _session.transactions[1].transaction_id


def login_sequence_retrieve():
    """
        Retrieve the current login sequence.
    """
    _session = current_session()

    if _session.account_id or _session.person_id:
        return (None, redirect(url_for('piko.profile')))

    if not len(_session.transactions) == 1:
        return (None, abort(500))

    return _session.transactions[0].transaction_id, _session.redirect


def login_sequence_start():
    """
        Start a login sequence.

        This function eliminates all
        :py:class:`piko.db.model.SessionTransaction` objects currently
        associated with the :py:class:`piko.db.model.Session`, inserts a new
        :py:class:`piko.db.model.SessionTransaction` and sets the redirect and
        expiry for the login sequence.
    """
    from piko.db import db
    from piko.db.model import SessionTransaction

    _session = current_session()
    _session.reset_transactions()
    _session.transactions = [SessionTransaction()]

    if request.args.get('next'):
        _session.redirect = request.args.get('next')
    elif request.referrer:
        _session.redirect = request.referrer
    else:
        _session.redirect = url_for('piko.profile')

    _session.expires = datetime.datetime.utcnow() + \
        datetime.timedelta(seconds=30)

    db.session.commit()

    return _session.transactions[0].transaction_id, _session.redirect
