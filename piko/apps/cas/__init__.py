"""
    Central Authentication Services for piko.
"""
import os

from flask import jsonify
from flask import request

from piko import App

# pylint: disable=invalid-name
template_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'templates'
    )
)

def register(apps):
    """
        Register CAS as a Flask application.

        :param apps:    A list of :py:class:`piko.App` applications.
        :type  apps:    list
        :returns:       A list of :py:class:`piko.App` applications with this
                        application included.
    """
    app = App('piko.cas', template_folder=template_path)
    app.debug = True
    register_routes(app)

    apps['/cas'] = app

    api_app = App('piko.api.v1.cas')
    api_app.debug = True
    register_api_routes(api_app)

    apps['/api/v1/cas'] = api_app

    return apps

def register_blueprint(app):
    """
        Register CAS as a Flask blueprint.
    """
    from piko import Blueprint

    blueprint = Blueprint(
        app,
        'piko.cas',
        __name__,
        url_prefix='/cas',
        template_folder=template_path
    )

    register_routes(blueprint)

    app.register_blueprint(blueprint)

    blueprint = Blueprint(
        app,
        'piko.api.v1.cas',
        __name__,
        url_prefix='/api/v1/cas'
    )

    register_api_routes(blueprint)

    app.register_blueprint(blueprint)

def register_routes(app):
    """
        Register routes for the UI.
    """
    @app.route('/')
    def dummy_index():
        """
            Dummy index
        """
        return app.abort(404)

def register_api_routes(app):
    """
        Register routes for the API v1.
    """
    @app.route('/saslauthd', methods=['POST'])
    # pylint: disable=unused-variable
    def saslauthd():
        """
            Authentication end-point for a Cyrus SASL Authentication daemon.
        """
        from piko.db import db
        from piko.db.model import Account

        try:
            username = request.form.get('_username', None)
            password = request.form.get('_password', None)
            # pylint: disable=unused-variable
            realm = request.form.get('_realm', None)

        # pylint: disable=broad-except
        except Exception, errmsg:
            if app.config.get('DEBUG', False):
                import traceback
                app.logger.error("Exception: %s" % (errmsg))
                app.logger.error("%s" % (traceback.format_exc()))

            return app.abort(403)

        if username is None or password is None:
            return app.abort(403)

        account = db.session.query(Account).filter_by(
            _name=username,
            type_name='email'
        ).first()

        if account is None:
            return app.abort(403)

        if account.person is None:
            return app.abort(403)

        result = account.person.verify_password(password)

        if result:
            return "OK"
        else:
            return app.abort(403)
