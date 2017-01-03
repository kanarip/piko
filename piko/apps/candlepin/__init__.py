import os

from flask import jsonify

from piko import App
from piko.authn import login_required
from piko.authz import role_required

template_path = os.path.abspath(
        os.path.join(
                os.path.dirname(__file__),
                'templates'
            )
    )

def register(apps):
    app = App('piko.candlepin', template_folder = template_path)
    app.debug = True
    register_routes(app)

    apps['/candlepin'] = app

    api_app = App('piko.api.v1.candlepin')
    api_app.debug = True
    register_api_routes(api_app)

    apps['/api/v1/candlepin'] = api_app

    return apps

def register_blueprint(app):
    from piko import Blueprint

    blueprint = Blueprint(
            app,
            'piko.candlepin',
            __name__,
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
    @app.route('/')
    def index():
        return app.render_template('index.html')

    @app.route('/register')
    @login_required
    def register():
        """
            A human being issues a command-line register.

            Award a token that can be used precisely once, and allows the system to be registered.
        """

        auth_token = "asd"

        return app.render_template(
                'register.html',
                auth_token = auth_token
            )

    @app.route('/admin')
    def admin():
        from piko.db import db

        from .db.model import Customer
        from .db.model import System

        customers = db.session.query(Customer).all()
        systems = db.session.query(System).all()

        return app.render_template(
                'admin/index.html',
                #dict(
                #        customers=customers,
                #        systems=systems
                #    )
                dict(
                        customers={},
                        systems={}
                    )
            )

    role_required(admin, 'candlepin_admin')

def register_api_routes(app):
    @app.route('/system/register', methods=['HEAD'])
    def system_register_head():
        return jsonify({'help doc': "some help"})

    @app.route('/system/register', methods=['POST'])
    def system_register():
        from piko.db import db
        from piko.db.model import System

        return jsonify({'result': True})
