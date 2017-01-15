"""
    candlepin.db.model.Subscription
    ===============================
"""
from datetime import datetime

from piko.db import db
from piko.utils import generate_int_id as generate_id


# pylint: disable=too-few-public-methods
class Subscription(db.Model):
    """
        .. TODO:: A class docstring
    """
    __tablename__ = 'candlepin_subscription'

    uuid = db.Column(db.Integer, primary_key=True)

    entitlement_id = db.Column(
        db.Integer,
        db.ForeignKey('candlepin_entitlement.uuid'),
        nullable=False
    )

    system_id = db.Column(
        db.String(36),
        db.ForeignKey('candlepin_system.uuid'),
        nullable=False
    )

    start_date = db.Column(db.DateTime, default=datetime.now)

    entitlement = db.relationship('Entitlement')
    system = db.relationship('System')

    def __init__(self, *args, **kwargs):
        super(Subscription, self).__init__(*args, **kwargs)

        uuid = generate_id()

        if db.session.query(Subscription).get(uuid) is not None:
            while db.session.query(Subscription).get(uuid) is not None:
                uuid = generate_id()

        self.uuid = uuid
