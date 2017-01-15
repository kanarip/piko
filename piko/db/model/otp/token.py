"""
    piko.db.model.OTPToken
    ======================

    A generic, abstract version of a token.
"""
from sqlalchemy.ext.declarative import declared_attr

from piko.db import db


class OTPToken(object):
    """
        OTPToken
    """
    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def uuid(cls):
        return db.Column(db.Integer, primary_key=True)

    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def name(cls):
        return db.Column(db.Unicode(64))

    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def type_name(cls):
        return db.Column(
            db.Enum('hotp', 'tan', 'totp'),
            default='totp',
            nullable=False
        )

    #: The associated account id
    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def account_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('account.uuid', ondelete="CASCADE")
        )

    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def account(cls):
        # pylint: disable=no-member
        return db.relationship('Account', backref=cls.__name__.lower())

    #: The associated person id
    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def person_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('person.uuid', ondelete="CASCADE")
        )

    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def person(cls):
        # pylint: disable=no-member
        return db.relationship('Person', backref=cls.__name__.lower())

    @declared_attr
    # pylint: disable=no-self-argument,missing-docstring
    def confirmed(cls):
        return db.Column(db.Boolean, default=False)
