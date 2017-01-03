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
from flask.ext.oauthlib.provider import OAuth2Provider

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
    oauth2 = OAuth2Provider(app)

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

    @app.route('/authorize', methods=["GET", "POST"])
    @oauth2.authorize_handler
    def authorize(*args, **kwargs):
        if request.method == "GET":
            return app.render_template('authorize.html')

        return True

    @app.route('/token')
    @oauth2.token_handler
    def token():
        return {}

    @app.route('/revoke')
    @oauth2.revoke_handler
    def revoke():
        pass

    @oauth2.clientgetter
    def get_client(client_id):
        from piko.db import db
        from piko.db.model import OAuth2Client

        return db.session.query(OAuth2Client).filter_by(client_id=client_id).first()

    @oauth2.grantgetter
    def get_grant(client_id, code):
        from piko.db import db
        from piko.db.model import OAuth2Grant

        return db.session.query(OAuthGrant).filter_by(client_id=client_id, code=code).first()

    @oauth2.tokengetter
    def get_token(access_token=None, refresh_token=None):
        from piko.db import db
        from piko.db.model import OAuth2Token

        if access_token:
            return db.session.query(OAuth2Token).filter_by(access_token=access_token).first()

        if refresh_token:
            return db.session.query(OAuth2Token).filter_by(refresh_token=refresh_token).first()

        return None

    @oauth2.grantsetter
    def set_grant(client_id, code, request, *args, **kwargs):
        from piko.db import db
        from piko.db.model import OAuth2Grant

        expires = datetime.utcnow() + timedelta(seconds=100)
        grant = OAuth2Grant(
                client_id=client_id,
                code=code['code'],
                redirect_uri=request.redirect_uri,
                scope=' '.join(request.scopes),
                user_id=g.user.id,
                expires=expires,
            )

        db.session.add(grant)
        db.session.commit()

    @oauth2.tokensetter
    def set_token(token, request, *args, **kwargs):
        from piko.db import db
        from piko.db.model import OAuth2Token

        # In real project, a token is unique bound to user and client.
        # Which means, you don't need to create a token every time.
        tok = OAuth2Token(**token)
        tok.user_id = request.user.id
        tok.client_id = request.client.client_id

        db.session.add(tok)
        db.session.commit()

    @oauth2.usergetter
    def get_user(username, password, *args, **kwargs):
        from piko.db import db
        from piko.db.model import Account

        # This is optional, if you don't need password credential
        # there is no need to implement this method
        return db.session.query(Account).filter_by(_name=username).first()

