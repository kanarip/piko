"""
    Candlepin application for ISV subscription management.
"""
import os

from flask import jsonify

from piko import App
from piko.authn import login_required
from piko.authz import role_required

# pylint: disable=invalid-name
template_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'templates'
    )
)


def register(apps):
    """
        Register candlepin as a Flask application.
    """
    app = App('piko.candlepin', template_folder=template_path)
    register_routes(app)

    apps['/candlepin'] = app

    api_app = App('piko.candlepin')
    api_app.debug = True
    register_api_routes(api_app)

    apps['/api/v1/candlepin'] = api_app

    return apps


def register_blueprint(app):
    """
        Register candlepin as a Flask blueprint.
    """
    from piko import Blueprint

    blueprint = Blueprint(
        app,
        'piko.candlepin',
        'piko.apps.candlepin',
        url_prefix='/candlepin',
        template_folder=template_path
    )

    register_routes(blueprint)

    app.register_blueprint(blueprint)

    blueprint = Blueprint(
        app,
        'piko.api.v1.candlepin',
        __name__,
        url_prefix='/api/v1/candlepin'
    )

    register_api_routes(blueprint)

    app.register_blueprint(blueprint)


def register_routes(app):
    """
        Register the routes with the main Flask application.
    """
    @app.route('/')
    # pylint: disable=unused-variable
    def index():
        """
            Index page.
        """
        # TODO: Should list customer entities the logged in human being is
        #       associated with, if the user is registered and logged in.
        return app.render_template('candlepin/index.html')

    @app.route('/register/customer')
    @login_required
    # pylint: disable=unused-variable
    def register_customer():
        """
            Register a customer entity through the web UI.
        """
        return app.render_template(
            'register/customer.html'
        )

    @app.route('/register/system')
    @login_required
    # pylint: disable=unused-variable
    def register_system():
        """
            Register a system through the web UI, such as may be necessary
            for off-line system registration.
        """

        # TODO: Obviously needs to be generated.
        auth_token = "asd"

        return app.render_template(
            'register/system.html',
            auth_token=auth_token
        )

    @app.route('/admin')
    def admin():
        """
            A fake admin interface.
        """
        return app.render_template(
            'admin/index.html',
            dict(
                customers={},
                systems={}
            )
        )

    role_required(admin, 'candlepin_admin')


def register_api_routes(app):
    """
        Register the routes with the main Flask application.
    """
    @app.route('/system/register', methods=['HEAD'])
    # pylint: disable=unused-variable
    def system_register_head():
        """
            Register a system with HTTP method `HEAD`.
        """
        return jsonify({'help doc': "some help"})

    @app.route('/system/register', methods=['POST'])
    # pylint: disable=unused-variable
    def system_register():
        """
            Register a system.
        """
        return jsonify({'result': True})
