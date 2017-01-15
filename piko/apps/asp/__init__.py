"""
    ASP Application
"""
import os

from piko.app import App

TEMPLATE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'templates'
    )
)


def register(apps):
    """
        Register this application as a Flask application.

        :param apps:    A list of :py:class:`piko.App` applications.
        :type  apps:    list
        :returns:       A list of :py:class:`piko.App` applications with this
                        application included.
    """
    app = App('piko.asp', template_folder=TEMPLATE_PATH)
    app.debug = True
    register_routes(app)

    apps['/asp'] = app

    return apps


def register_blueprint(app):
    """
        Register this application as a Flask blueprint.
    """
    from piko import Blueprint
    blueprint = Blueprint(app, 'piko.asp', __name__, url_prefix='/asp')

    register_routes(blueprint)

    app.register_blueprint(blueprint)

    blueprint = Blueprint(
        app,
        'piko.api.v1.asp',
        __name__,
        url_prefix='/api/v1/asp'
    )

    register_api_routes(blueprint)

    app.register_blueprint(blueprint)


def register_routes(app):
    """
        Register routes with the main Flask application.
    """
    @app.route('/')
    # pylint: disable=unused-variable
    def index():
        """
            Dummy.
        """
        return app.abort(404)


def register_api_routes(app):
    """
        Register API routes with the main Flask application.
    """
    @app.route('/')
    # pylint: disable=unused-variable
    def index():
        """
            Dummy.
        """
        return app.abort(404)
