import os

from piko import App

template_path = os.path.abspath(
        os.path.join(
                os.path.dirname(__file__),
                'templates'
            )
    )

def register(apps):
    app = App('piko.busby', template_folder = template_path)
    app.debug = True
    register_routes(app)

    apps['/busby'] = app

    return apps

def register_blueprint(app):
    from piko import Blueprint

    blueprint = Blueprint(
            app,
            'piko.busby',
            __name__,
            url_prefix='/busby',
            template_folder=template_path
        )

    register_routes(blueprint)

    app.register_blueprint(blueprint)

def register_routes(app):
    @app.route('/')
    def index():
        return app.render_template('busby/index.html')
