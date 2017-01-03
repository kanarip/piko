import gevent
import json
import os

from flask import flash
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

template_path = os.path.abspath(
        os.path.join(
                os.path.dirname(__file__),
                'templates'
            )
    )

def register(apps):
    app = App('piko', template_folder = template_path)
    app.debug = True
    register_routes(app)

    apps['/'] = app

    return apps

def register_blueprint(app):
    from piko import Blueprint
    blueprint = Blueprint(app, 'piko', __name__)

    register_routes(blueprint)

    app.register_blueprint(blueprint)

def register_routes(app):
    @app.route('/')
    def index():
        """
            Nothing much to see here.
        """
        return app.render_template('index.html')

    @app.route('/login')
    def login():
        """
            Renders the login overview with links to enabled login
            mechanisms.
        """
        return app.render_template('login/index.html')

    @app.route('/login/complete')
    def login_complete():
        from piko.db import db
        from piko.db.model import Person

        _session = current_session()
        person = db.session.query(Person).get(_session.person_id)

        if person is None:
            return app.abort(500, "Invalid Person.")

        task_id = _session.transactions[0].task_id

        if task_id is None:
            return app.abort(500, "Invalid Task.")

        task = check_password_hash.AsyncResult(task_id)

        if task is None:
            return app.abort(403, "Access Denied")

        if task.info == True:
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

    @app.route('/login/email', methods = ['GET', 'POST'])
    def login_email():
        from piko.forms import LoginEmailForm

        _session = current_session()

        # Already logged in.
        if _session.person_id == session.get('person_id', False):
            if _session.id == session.get('uuid'):
                return redirect(url_for('piko.profile'))

        if request.method == 'GET':
            uuid, _redirect = login_sequence_start()

            form = LoginEmailForm(request.form, uuid = uuid)

            return app.render_template('login/email.html', form = form)

        elif request.method == 'POST':
            uuid, _redirect = login_sequence_retrieve()

            if not request.form.get('uuid') == uuid:
                return _redirect or app.abort(500)

            form = LoginEmailForm(request.form, uuid = uuid)

            if form.validate():
                from piko.db import db
                from piko.db.model import Account

                account = db.session.query(
                        Account
                    ).filter_by(
                            _name=form.email_address.data,
                            type_name='email'
                        ).first()

                # No such account could be found.
                if account is None:
                    flash(_("Login failed."), 'danger')
                    return login_sequence_complete(False)

                login_sequence_associate_account(account.id)

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

                result = account.person.verify_password(
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

            return app.render_template('login/email.html', form=form)

        else:
            return app.abort(405)

        return redirect(url_for('piko.login'))

    @app.route('/login/otp', methods = [ 'GET', 'POST' ])
    def login_otp():
        from piko.forms import LoginOTPForm

        from piko.db import db
        from piko.db.model import Person

        _session = current_session()

        if _session.person_id == session.get('person_id', None):
            if _session.id == session.get('uuid'):
                return redirect(url_for('piko.index'))

        form = LoginOTPForm(
                request.form,
                uuid = _session.transactions[1].transaction_id
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

                if person == None:
                    app.logger.error("no person for _session.person_id: %r" % (_session.person_id))
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
                        app.logger.info("setting session['person_id'] to %r" % (person.id))

                        session['person_id'] = person.id
                        app.logger.info("using session's redirect %r" % (_session.redirect))
                        _redirect = redirect(_session.redirect)
                        _session.redirect = None

                        login_sequence_complete(True)

                        return _redirect

                    task = check_password_hash.AsyncResult(task_id)

                    task.wait()

                    if task.info == True:
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

                return app.render_template('login/otp.html', form = form)
        else:
            return app.abort(405)

    @app.route('/login/verify/<string:task_id>')
    def login_verify(task_id):
        app.logger.info("Verifying status of task ID %s" % (task_id))

        def event_stream():
            task = check_password_hash.AsyncResult(task_id)

            if task is None:
                yield 'data: %s\n\n' % (
                        json.dumps(
                                { "result": False }
                            )
                    )

            while True:
                gevent.sleep(1)

                if task.state == "PENDING":
                    yield 'data: %s\n\n' % (
                            json.dumps(
                                    { "result": None }
                                )
                        )

                else:
                    yield 'data: %s\n\n' % (
                            json.dumps(
                                    { "result": True }
                                )
                        )

                    break

        return Response(
                event_stream(),
                mimetype='text/event-stream'
            )

    @app.route('/login/wait')
    def login_wait():
        from piko.db import db
        from piko.db.model import Person

        _session = current_session()
        person = db.session.query(Person).get(_session.person_id)

        if person is None:
            app.logger.error("no person for _session.person_id: %r" % (_session.person_id))
            return app.abort(500)
        else:
            app.logger.info("person ID %r" % (_session.person_id))

        task_id = _session.transactions[0].task_id

        return app.render_template('login/wait.html', task_id=task_id)

    @login_required
    @app.route('/logout')
    def logout():
        return app.render_template('index.html')

    @login_required
    @app.route('/profile')
    def profile():
        return app.render_template('index.html')

