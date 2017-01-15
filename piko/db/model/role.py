"""
    .. TODO:: A module docstring.
"""
from piko.db import db


# pylint: disable=too-few-public-methods
class Role(db.Model):
    """
        A role.
    """

    __tablename__ = "role"

    uuid = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(16), nullable=False)
    name = db.Column(db.String(64), nullable=False)

    description = db.Column(
        db.Text,
        default='This role has no description set.'
    )

    ldap_role = db.Column(db.Boolean, default=False)
    ldap_role_dn = db.Column(db.String(256), nullable=True, default=None)
