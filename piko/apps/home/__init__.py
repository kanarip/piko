"""
    The main piko application homepage.
"""
import json
import os

import gevent

from flask import flash
from flask import jsonify
from flask import redirect
from flask import _request_ctx_stack
from flask import request
from flask import Response
from flask import send_from_directory
from flask import session
from flask import url_for

from piko import App
from piko.authn import current_session
from piko.authn import login_required
from piko.authn import login_sequence_associate_account
from piko.authn import login_sequence_associate_person
from piko.authn import login_sequence_complete
from piko.authn import login_sequence_continue
from piko.authn import login_sequence_start
from piko.authn import login_sequence_retrieve

from piko.bcrypt import check_password_hash

from piko.l10n import get_babel_locale

from piko.translate import _

# pylint: disable=invalid-name
template_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'templates'
    )
)


def register(apps):
    """
        Register home as a Flask application.

        :param apps:    A list of :py:class:`piko.App` applications.
        :type  apps:    list
        :returns:       A list of :py:class:`piko.App` applications with this
                        application included.
    """
    app = App('piko', template_folder=template_path)
    app.debug = True
    register_routes(app)

    apps['/'] = app

    return apps


def register_blueprint(app):
    """
        Register home as a Flask blueprint.
    """
    from piko import Blueprint
    blueprint = Blueprint(
        app,
        'piko',
        __name__,
        url_prefix=''
    )

    register_routes(blueprint)

    app.register_blueprint(blueprint)

    blueprint = Blueprint(
        app,
        'piko.api.v1',
        __name__,
        url_prefix='/api/v1'
    )

    register_api_routes(blueprint)

    app.register_blueprint(blueprint)


def register_routes(app):
    """
        Register routes with the main Flask application.
    """
    @app.route('/')
    # pylint: disable=unused-variable
    def index():
        """
            Nothing much to see here.
        """
        from piko.db import db
        from piko.db.model import Product

        products = db.session.query(Product).options(
            db.joinedload(
                Product.translations[get_babel_locale()]
            )
        ).filter_by(signup_enabled=True).all()

        return app.render_template(
            'index.html',
            products=products
        )

    @app.route('/login')
    # pylint: disable=unused-variable
    def login():
        """
            Renders the login overview with links to enabled login
            mechanisms.
        """
        _redirect = request.args.get('next') or request.referrer

        _session = current_session()

        if _session is not None:
            _session.set_redirect(_redirect)

        return app.render_template('login/index.html')

    @app.route('/login/complete')
    # pylint: disable=unused-variable
    def login_complete():
        """
            A login sequence is completed.
        """
        from piko.db import db
        from piko.db.model import Person

        _session = current_session()

        if _session.person_id is None:
            return app.abort(403)

        person = db.session.query(Person).filter_by(
            uuid=_session.person_id
        ).first()

        if person is None:
            return app.abort(500, _("Invalid Person."))

        task_id = _session.transactions[0].task_id

        if task_id is None:
            return app.abort(500, "Invalid Task.")

        task = check_password_hash.AsyncResult(task_id)

        if task is None:
            return app.abort(403, "Access Denied")

        if task.info is True:
            # We need not to.
            # session['person_id'] = person.uuid

            if _session.redirect:
                _redirect = redirect(_session.redirect)
            else:
                _redirect = redirect(url_for('piko.index'))

            login_sequence_complete(True)

            return _redirect

        else:
            login_sequence_complete(False)

            return app.abort(500)

    @app.route('/login/email', methods=['GET', 'POST'])
    # pylint: disable=unused-variable
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    def login_email():
        """
            Login with an email address and a password.

            #.  Accepts GET and POST requests.

            #.  Continues an existing login sequence.

            #.  Verifies the user is not already logged in, or
                redirects to profile (with a flash).
        """
        from piko.forms import LoginEmailForm

        _session = current_session()

        # Already logged in.
        if _session.person_id is not None:
            if _session.person_id == session.get('person_id', False):
                if _session.uuid == session.get('uuid'):
                    flash(_("Already logged in."), 'danger')
                    return redirect(url_for('piko.profile'))

        if request.method == 'GET':
            uuid, _redirect = login_sequence_start()

            form = LoginEmailForm(request.form, uuid=uuid)

            return app.render_template('login/email.html', form=form)

        elif request.method == 'POST':
            uuid, _redirect = login_sequence_retrieve()

            if not request.form.get('uuid') == uuid:
                return app.abort(403, _("Invalid submission."))

            form = LoginEmailForm(request.form, uuid=uuid)

            if form.validate():
                from piko.db import db
                from piko.db.model import Account

                account = db.session.query(Account).filter_by(
                    _name=form.email_address.data,
                    type_name='email'
                ).first()

                # No such account could be found.
                if account is None:
                    flash(_("Login failed."), 'danger')
                    return login_sequence_complete(False)

                login_sequence_associate_account(account.uuid)

                # This account is not a personal account.
                if account.person_id is None:
                    flash(_("Login failed."), 'danger')
                    return login_sequence_complete(False)

                # Associate the account we've just attempted to login
                # with.
                #
                # This does not set any validity.
                login_sequence_associate_person(account.person_id)

                # Associate a translaction uuid with the current state
                # of progress.
                transaction, uuid = login_sequence_continue()

                account.person.verify_password(
                    form.password.data,
                    transaction=transaction
                )

                if len(account.second_factors) > 0:
                    return redirect(url_for('piko.login_otp'))

                elif len(account.person.second_factors) > 0:
                    return redirect(url_for('piko.login_otp'))

                else:
                    return redirect(url_for('piko.login_wait'))

            else:
                flash(_("Login failed"), 'danger')
                return redirect(url_for('piko.login'))

            return app.render_template('login/email.html', form=form)

        else:
            return app.abort(405)

        return redirect(url_for('piko.login'))

    @app.route('/login/otp', methods=['GET', 'POST'])
    # pylint: disable=unused-variable
    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    def login_otp():
        """
            Continue a login sequence by requesting an OTP be entered in to
            a form.
        """
        from piko.forms import LoginOTPForm

        from piko.db import db
        from piko.db.model import Person

        _session = current_session()

        if _session.person_id is None:
            return redirect(url_for('piko.login'))

        if _session.person_id == session.get('person_id', False):
            if _session.uuid == session.get('uuid'):
                return redirect(url_for('piko.login'))

        form = LoginOTPForm(
            request.form,
            uuid=_session.transactions[1].transaction_id
        )

        if request.method == 'GET':
            return app.render_template('login/otp.html', form=form)

        elif request.method == "POST":
            assert len(_session.transactions) > 1

            transaction_id = _session.transactions[1].transaction_id
            uuid = request.form.get('uuid')

            if not uuid == transaction_id:
                app.logger.error("form's uuid is not session transaction id")
                return app.abort(500, "Invalid transaction UUID")

            if form.validate():
                person = db.session.query(
                    Person
                ).get(_session.person_id)

                if person is None:
                    app.logger.error(
                        "no person for _session.person_id: %r" % (
                            _session.person_id
                        )
                    )

                    return app.abort(500)
                else:
                    app.logger.info("person ID %r" % (_session.person_id))

                result = person.validate_token(form.otp.data)

                if result:
                    app.logger.info("token validated")
                else:
                    app.logger.error("token invalid")

                if not result:
                    flash(_("Login failed"), 'danger')

                    login_sequence_complete(False)

                    return redirect(url_for('piko.login'))

                else:
                    flash(_("Login successful"), 'success')
                    task_id = _session.transactions[0].task_id

                    if not task_id:
                        app.logger.info(
                            "setting session['person_id'] to %r" % (person.id)
                        )

                        session['person_id'] = person.id

                        app.logger.info(
                            "using session's redirect %r" % (_session.redirect)
                        )

                        _redirect = redirect(_session.redirect)
                        _session.redirect = None

                        login_sequence_complete(True)

                        return _redirect

                    task = check_password_hash.AsyncResult(task_id)

                    task.wait()

                    if task.info is True:
                        session['person_id'] = person.id

                        if _session.redirect:
                            _redirect = redirect(_session.redirect)
                        else:
                            _redirect = redirect(url_for('piko.index'))

                        login_sequence_complete(True)

                        return _redirect

                    else:
                        login_sequence_complete(False)

                        return app.abort(500)

            else:
                person = db.session.query(Person).get(_session.person_id)

                if person is None:
                    return app.abort(500)

                login_sequence_complete(False)

                return app.render_template('login/otp.html', form=form)
        else:
            return app.abort(405)

    @app.route('/login/verify/<string:task_id>')
    # pylint: disable=unused-variable
    def login_verify(task_id):
        """
            Verify the login
        """
        app.logger.info("Verifying status of task ID %s" % (task_id))

        def event_stream():
            """
                This is used to continuously track progress.
            """
            task = check_password_hash.AsyncResult(task_id)

            if task is None:
                yield 'data: %s\n\n' % (
                    json.dumps({"result": False})
                )

            while True:
                gevent.sleep(1)

                if task.state == "PENDING":
                    yield 'data: %s\n\n' % (
                        json.dumps({"result": None})
                    )

                else:
                    yield 'data: %s\n\n' % (
                        json.dumps({"result": True})
                    )

                    break

        return Response(
            event_stream(),
            mimetype='text/event-stream'
        )

    @app.route('/login/wait')
    # pylint: disable=unused-variable
    def login_wait():
        """
            This page is used to let the user wait for the login
            verification.
        """
        from piko.db import db
        from piko.db.model import Person

        _session = current_session()

        if _session.person_id is None:
            return app.abort(403)

        person = db.session.query(Person).get(_session.person_id)

        if person is None:
            app.logger.error(
                "no person for _session.person_id: %r" % (_session.person_id)
            )

            return app.abort(500)
        else:
            app.logger.info("person ID %r" % (_session.person_id))

        task_id = _session.transactions[0].task_id

        return app.render_template('login/wait.html', task_id=task_id)

    @login_required
    @app.route('/logout')
    # pylint: disable=unused-variable
    def logout():
        """
            Logout a user.

            .. TODO:: Doesn't seem to actually do too much.
        """

        from piko.db import db

        _session = current_session()

        db.session.delete(_session)

        session.clear()

        db.session.commit()

        flash(_("You are now logged out."))

        return redirect(url_for('piko.logout_ok'))

    @app.route('/logout/ok')
    # pylint: disable=unused-variable
    def logout_ok():
        """
            Confirm the user is logged out.
        """
        return app.render_template('logout.html')

    @login_required
    @app.route('/profile')
    # pylint: disable=unused-variable
    def profile():
        """
            Render a user's profile.
        """
        return app.render_template('index.html')


def register_api_routes(app):
    """
        Register the routes for the API.
    """
    @app.route('/whoami', methods=['POST'])
    # pylint: disable=unused-variable
    def whoami():
        """
            Returns information about who the client user is.

            .. TODO::

                This should actually do the thing for the actual user.
        """
        return jsonify({'result': True, 'username': 'john.doe@example.org'})

    @app.route('/account-info', methods=['POST'])
    # pylint: disable=unused-variable
    def account_info():
        """
            Let the user know just about everything about their account that
            is somehow valuable information.
        """
        from piko.db import db
        from piko.db.model import Account

        data = json.loads(request.data)

        account = db.session.query(Account).filter_by(
            _name=data["username"]
        ).first()

        if account is None:
            return app.abort(404)

        person = None
        if account.person is not None:
            person = account.person.to_dict()

        return jsonify(result=True, account=account.to_dict(), person=person)
