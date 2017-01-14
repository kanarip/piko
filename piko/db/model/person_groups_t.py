"""
    .. TODO:: A module docstring.
"""
from piko.db import db

# pylint: disable=invalid-name
person_groups_t = db.Table(
    'person_groups',
    db.Column('person_id', db.Integer, db.ForeignKey('person._id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group._id'))
)
