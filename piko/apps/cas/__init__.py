import os

from flask import jsonify

from piko import App

template_path = os.path.abspath(
        os.path.join(
                os.path.dirname(__file__),
                'templates'
            )
    )

def register(apps):
    app = App('piko.cas', template_folder = template_path)
    app.debug = True
    register_routes(app)

    apps['/cas'] = app

    api_app = App('piko.api.v1.cas')
    api_app.debug = True
    register_api_routes(api_app)

    apps['/api/v1/cas'] = api_app

    return apps

def register_blueprint(app):
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
    pass

def register_api_routes(app):
    @app.route('/', methods = [ 'POST' ])
    def index():
        return jsonify({
                'result': True
            })
