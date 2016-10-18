import os

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

def register_routes(app):
    @app.route('/')
    def index():
        return app.render_template('index.html')

    @app.route('/register', methods = [ 'POST' ])
    def register():
        """
            A human being issues a command-line register.
        """
        return "magic token"

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
