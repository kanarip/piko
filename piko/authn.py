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

from flask import abort
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from functools import wraps

def current_session():
    """
        Return the current session as recorded in the database, or record
        the current session in the database.

        :returns:   A :py:class:`piko.db.model.Session` object.
    """
    from piko.db import db
    from piko.db.model import Session

    _session = db.session.query(Session).filter_by(id=session.get('uuid', None)).first()

    if _session == None:
        db.session.add(Session(id=session.get('uuid')))
        db.session.commit()
        _session = db.session.query(Session).filter_by(id=session.get('uuid', None)).first()

    return _session

def login_required(f):
    """
        Decorator function for route controllers that require a login.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.get('user', None) == None:
            return redirect(url_for('piko.login', next=request.url))

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
    from piko.db.model import AccountLogin

    account = db.session.query(Account).filter_by(remote_id=remote_id, type_name=type_name).first()
    if account == None:
        account = Account(
                name        = name,
                remote_id   = remote_id,
                type_name   = type_name,
                locale      = get_babel_locale().__str__(),
                timezone    = get_babel_timezone().__str__()
            )

        db.session.add(account)
        db.session.commit()
        account = db.session.query(Account).filter_by(remote_id=remote_id, type_name=type_name).first()
    else:
        account.name = name

        if len(account.second_factors) > 0:
            session['_flashes'] = []

            login_sequence_associate_account(account.id)

            transaction, uuid = login_sequence_continue()

            return redirect(url_for('piko.login_otp'))

    _session = current_session()

    _session.account_id = account.id
    session['account_id'] = account.id

    return login_sequence_complete(True)

def login_sequence_associate_account(id):
    """
        Associate an :py:attr:`piko.db.model.Account.id` with the
        current :py:attr:`piko.db.model.Session`, without disclosing
        the validity of the account to the visitor via, for example, a
        cookie value.

        This is used for staged account login processing -- we keep the
        information about a user having attempted to login with an
        otherwise valid account on the server.
    """
    from piko.db import db
    _session = current_session()
    _session.account_id = id
    db.session.commit()

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

    if not _session.account_id or not len(_session.transactions) in range(1,3):
        session.clear()
        db.session.delete(_session)
        db.session.commit()
        return abort(500)

    # Reset all ongoing transactions regardless of success or failure.
    _session.reset_transactions()

    # Store the current redirect.
    _redirect = _session.redirect

    # Zero out the stored redirect.
    _session.redirect = None

    # Store the record on the login attempt.
    db.session.add(
            AccountLogin(
                    account_id = _session.account_id,
                    success = success
                )
        )

    if not success:
        db.session.delete(_session)
        db.session.commit()
        session.clear()
        _redirect = url_for('piko.login')

    db.session.commit()

    return redirect(_redirect)

def login_sequence_continue():
    """
        Mark the session with a second transaction, such as for a TOTP/HOTP/TAN sequence.

        Returns the transaction to associate the validation of the current credentials to,
        which can be an asynchronous :py:class:`celery.Celery` task, for which we store
        the task ID as part of the transaction.

        Also returns the uuid for the new form.

        :returns:   A tuple of the :py:class:`piko.db.model.SessionTransaction` object
                    for the entry event, and the :py:class:`uuid.UUID`.
    """

    from piko.db import db
    from piko.db.model import SessionTransaction

    _session = current_session()

    if not _session.account_id:
        return (None, abort(500))

    if len(_session.transactions) == 2:
        return _session.transactions[0], _session.transactions[1].transaction_id

    _session.transactions.append(SessionTransaction())

    db.session.commit()

    return _session.transactions[0], _session.transactions[1].transaction_id

def login_sequence_retrieve():
    from piko.db import db
    _session = current_session()

    if _session.account_id:
        return (None, redirect(url_for('piko.profile')))

    if not len(_session.transactions) == 1:
        return (None, abort(500))

    return _session.transactions[0].transaction_id, _session.redirect

def login_sequence_start():
    """
        Start a login sequence.

        This function eliminates all :py:class:`piko.db.model.SessionTransaction` objects
        currently associated with the :py:class:`piko.db.model.Session`, inserts a new
        :py:class:`piko.db.model.SessionTransaction` and sets the redirect and expiry for
        the login sequence.
    """
    from piko.db import db
    from piko.db.model import SessionTransaction

    _session = current_session()
    _session.reset_transactions()
    _session.transactions = [ SessionTransaction() ]
    _session.redirect = request.args.get('next') or request.referrer or url_for('piko.profile')
    _session.expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    db.session.commit()

    return _session.transactions[0].transaction_id, _session.redirect

