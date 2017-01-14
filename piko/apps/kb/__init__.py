"""
    Knowledgebase application for providers of products.
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
        Register the knowledgebase as a Flask application.
    """
    app = App('piko.kb', template_folder=template_path)
    register_routes(app)

    apps['/kb'] = app

    return apps

def register_blueprint(app):
    """
        Register the knowledgebase as a Flask blueprint.
    """
    from piko import Blueprint

    blueprint = Blueprint(
        app,
        'piko.kb',
        'piko.apps.kb',
        url_prefix='/kb',
        template_folder=template_path
    )

    register_routes(blueprint)

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
        return app.render_template('kb/index.html')
