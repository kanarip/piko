"""
    candlepin.db.model.Subscription
    ===============================
"""
from datetime import datetime
from uuid import uuid4

from piko.db import db


# pylint: disable=too-few-public-methods
class Subscription(db.Model):
    """
        .. TODO:: A class docstring
    """
    __tablename__ = 'candlepin_subscription'

    _id = db.Column(db.Integer, primary_key=True)

    entitlement_id = db.Column(
        db.Integer,
        db.ForeignKey('candlepin_entitlement._id'),
        nullable=False
    )

    system_id = db.Column(
        db.Integer,
        db.ForeignKey('candlepin_system._id'),
        nullable=False
    )

    start_date = db.Column(db.DateTime, default=datetime.now)

    entitlement = db.relationship('Entitlement')
    system = db.relationship('System')

    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)

        # pylint: disable=no-member
        _id = (int)(uuid4().int / 2**97)

        if db.session.query(Subscription).get(_id) is not None:
            while db.session.query(Subscription).get(_id) is not None:
                # pylint: disable=no-member
                _id = (int)(uuid4().int / 2**97)

        self._id = _id
