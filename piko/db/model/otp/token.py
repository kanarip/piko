import datetime
import uuid

from sqlalchemy.ext.declarative import declared_attr

from piko.db import db

class OTPToken(object):
    @declared_attr
    def id(cls):
        return db.Column(db.Integer, primary_key=True)

    @declared_attr
    def name(cls):
        return db.Column(db.Unicode(64))

    @declared_attr
    def type_name(cls):
        return db.Column(db.Enum('hotp', 'tan', 'totp'), default='totp', nullable=False)

    #: The associated account id
    @declared_attr
    def account_id(cls):
        return db.Column(db.Integer, db.ForeignKey('account.id', ondelete="CASCADE"))

    @declared_attr
    def account(cls):
        return db.relationship('Account', backref=cls.__name__.lower())

    @declared_attr
    def confirmed(cls):
        return db.Column(db.Boolean, default=False)
