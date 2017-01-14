"""
    .. TODO:: A module docstring.
"""
from piko.db import db

# pylint: disable=invalid-name
account_roles_t = db.Table(
    'account_roles',
    db.Column('account_id', db.Integer, db.ForeignKey('account._id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role._id'))
)
