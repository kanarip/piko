import datetime
import os
import uuid

from flask import Blueprint
from flask import flash
from flask import redirect
from flask import request
from flask import session
from flask import url_for
from flask.ext.oauthlib.client import OAuthException

from piko.authn import current_session
from piko.authn import login_sequence_account_get_or_create
from piko.authn import login_sequence_associate_account
from piko.authn import login_sequence_complete
from piko.authn import login_sequence_continue
from piko.authn import login_sequence_retrieve
from piko.authn import login_sequence_start

from piko.l10n import get_babel_locale
from piko.l10n import get_babel_timezone

from piko.db import db
from piko.db.model import Account
from piko.db.model import SessionTransaction

from piko.translate import _

from .facebook import facebook
from .google import google
from .twitter import twitter

template_path = os.path.abspath(
        os.path.join(
                os.path.dirname(__file__),
                'templates'
            )
    )

def register(apps): 
    from piko import App
    app = App('piko.oauth', template_folder = template_path)
    app.debug = True
    register_routes(app)
    apps['/oauth'] = app
    return apps

def register_blueprint(app):
    from piko import Blueprint
    blueprint = Blueprint(app, 'piko.oauth', __name__, url_prefix='/oauth')
    register_routes(blueprint)
    app.register_blueprint(blueprint)

def register_routes(app):
    @app.route('/')
    def index():
        return app.abort(404)

    @app.route('/facebook/login')
    def oauth_facebook_login():
        """
            Authentication against Facebook starts here.

            .. IMPORTANT::

                The callback URL **MUST** be randomized (say, through a
                session UUID or CSRF token, but not either of those two),
                or the fact a visitor is allowed to authenticate using
                the third party establishes an exploit path -- the third
                party holds all the data necessary to authenticate on the
                user's behalf and fully controls the infrastructure against
                which the user must hypothetically authenticate.
        """

        uuid, redirect = login_sequence_start()

        callback = url_for(
                'piko.oauth.oauth_facebook_authenticate',
                uuid = uuid,
                _external = True,
                next = redirect
            )

        return facebook().authorize(callback=callback)

    @app.route('/facebook/authenticate/<uuid>')
    def oauth_facebook_authenticate(uuid=None):
        """
            This is the callback URL to which the user is redirected
            after successfully authenticating against Facebook.
        """

        if uuid == None or len(uuid) is not 36:
            return app.abort(401)

        _session = current_session()
        _uuid, redirect = login_sequence_retrieve()

        if not uuid == _uuid:
            return app.abort(401)

        _facebook = facebook()
        resp = _facebook.authorized_response()

        if resp is None:
            return login_sequence_complete(False)

        if isinstance(resp, OAuthException):
            return app.abort(503)

        session['facebook_oauth_token'] = (resp['access_token'], '')

        flash(_("Login successful"), 'success')

        me = _facebook.get('/me')

        return login_sequence_account_get_or_create('facebook', me.data['id'], me.data['name'])

    @app.route('/google/login')
    def oauth_google_login():
        """
            Authentication against Google starts here.

            .. IMPORTANT::

                The callback URL **MUST** be randomized (say, through a
                session UUID or CSRF token, but not either of those two),
                or the fact a visitor is allowed to authenticate using
                the third party establishes an exploit path -- the third
                party holds all the data necessary to authenticate on the
                user's behalf and fully controls the infrastructure against
                which the user must hypothetically authenticate.
        """
        uuid, redirect = login_sequence_start()

        callback = url_for(
                'piko.oauth.oauth_google_authenticate',
                uuid = uuid,
                _external = True,
                next = redirect
            )

        return google().authorize(callback=callback)

    @app.route('/google/authenticate/<uuid>')
    def oauth_google_authenticate(uuid=None):
        """
            This is the callback URL to which the user is redirected
            after successfully authenticating against Google.
        """

        if uuid == None or len(uuid) is not 36:
            return app.abort(401)

        _session = current_session()
        _uuid, redirect = login_sequence_retrieve()

        if not uuid == _uuid:
            return app.abort(401)

        _google = google()
        resp = _google.authorized_response()

        if resp is None:
            return login_sequence_complete(False)

        if isinstance(resp, OAuthException):
            return app.abort(503)

        session['google_oauth_token'] = (resp['access_token'],)

        flash(_("Login successful"), 'success')

        me = _google.get('userinfo')

        return login_sequence_account_get_or_create('google', me.data['id'], me.data['name'])

    @app.route('/twitter/login')
    def oauth_twitter_login():
        """
            Authentication against Twitter starts here.

            .. IMPORTANT::

                The callback URL **MUST** be randomized (say, through a
                session UUID or CSRF token, but not either of those two),
                or the fact a visitor is allowed to authenticate using
                the third party establishes an exploit path -- the third
                party holds all the data necessary to authenticate on the
                user's behalf and fully controls the infrastructure against
                which the user must hypothetically authenticate.
        """
        uuid, redirect = login_sequence_start()

        callback = url_for(
                'piko.oauth.oauth_twitter_authenticate',
                uuid = uuid,
                _external = True,
                next = redirect
            )

        return twitter().authorize(callback=callback)

    @app.route('/twitter/authenticate/<uuid>')
    def oauth_twitter_authenticate(uuid=None):
        """
            This is the callback URL to which the user is redirected
            after successfully authenticating against Facebook.
        """

        if uuid == None or len(uuid) is not 36:
            return app.abort(401)

        _session = current_session()
        _uuid, redirect = login_sequence_retrieve()

        if not uuid == _uuid:
            return app.abort(401)

        _twitter = twitter()
        resp = _twitter.authorized_response()

        if resp is None:
            return login_sequence_complete(False)

        if isinstance(resp, OAuthException):
            return app.abort(503)

        session['twitter_oauth_token'] = resp

        flash(_("Login successful"), 'success')

        return login_sequence_account_get_or_create('twitter', resp['user_id'], resp['screen_name'])

