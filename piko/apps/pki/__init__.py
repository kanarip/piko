"""
    piko.apps.pki
    =============
"""
import os

from flask import abort
from flask import Response

from piko import App

TEMPLATE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        'templates'
    )
)


def register(apps):
    """
        Register the application
    """
    app = App('piko.pki', template_folder=TEMPLATE_PATH)
    app.debug = True
    register_routes(app)

    apps['/pki'] = app

    return apps


def register_blueprint(app):
    """
        Register a blueprint with the application
    """
    from piko import Blueprint

    blueprint = Blueprint(
        app,
        'piko.pki',
        __name__,
        url_prefix='/pki',
        template_folder=TEMPLATE_PATH
    )

    register_routes(blueprint)

    app.register_blueprint(blueprint)


def register_routes(app):
    """
        Register regular UI routes
    """
    # TODO: Require authentication
    # TODO: Require ownership of the system, or admin role
    @app.route('/revoke/<system_uuid>')
    # pylint: disable=unused-variable
    def request(system_uuid):
        """
            Request a certificate for a system.
        """
        from piko.db import db
        from piko.apps.pki.db.model import Certificate
        from piko.apps.candlepin.db.model import System

        system = db.session.query(System).filter_by(uuid=system_uuid).first()

        if system is None:
            # TODO: Obscure the message
            return abort(404, "No such system")

        cert = db.session.query(Certificate).filter_by(cn=system_uuid).first()

        if cert is None:
            # TODO: Obscure the message
            return abort(404, "No such certificate")

        return dict()

    # TODO: Require authentication
    @app.route('/download/<system_uuid>')
    # pylint: disable=unused-variable
    def download(system_uuid):
        """
            Let a system download a certificate + key in PEM encoding
        """
        from piko.db import db
        from piko.apps.pki.db.model import Certificate
        from piko.apps.candlepin.db.model import System

        system = db.session.query(System).filter_by(uuid=system_uuid).first()

        if system is None:
            # TODO: Obscure the message
            return abort(404, "No such system")

        cert = db.session.query(Certificate).filter_by(cn=system_uuid).first()

        if cert is None:
            # TODO: Obscure the message
            return abort(404, "No such certificate")

        return Response(
            cert.certificate + cert.private_key,
            mimetype='text/plain'
        )
