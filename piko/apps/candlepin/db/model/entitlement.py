"""
    candlepin.db.model.Entitlement
    ==============================
"""
import calendar
from datetime import datetime
from datetime import timedelta
from uuid import uuid4
from piko.db import db


def in_two_months(start=None):
    """
        Two months from whatever you define as the start.
    """
    if start is None:
        start = datetime.utcnow()

    cur_year = (int)(datetime.utcnow().strftime('%Y'))
    cur_month = (int)(datetime.utcnow().strftime('%m'))
    days_this_month = calendar.monthrange(cur_year, cur_month)[1]
    days_next_month = calendar.monthrange(cur_year, cur_month + 1)[1]

    total_days = days_this_month + days_next_month

    delta = timedelta(days=total_days)

    return start + delta


# pylint: disable=too-few-public-methods
class Entitlement(db.Model):
    """
        An entitlement for a customer
    """
    __tablename__ = 'candlepin_entitlement'

    #: The ID for the entitlement
    _id = db.Column(db.Integer, primary_key=True)

    #: The ID of the customer this entitlement is associated with.
    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('candlepin_customer._id', ondelete='CASCADE'),
        nullable=False
    )

    #: The product ID this entitlement allows the customer to install,
    #: if any one particular product in particular.
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('candlepin_product._id', ondelete='CASCADE'),
        nullable=True
    )

    #: The quantity
    quantity = db.Column(db.Integer, default=-1)

    #: The start date of the entitlement
    start_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    #: Validity ends this many days after the start date
    end_date = db.Column(
        db.DateTime,
        default=in_two_months,
        nullable=False
    )

    #: Proxy attribute
    customer = db.relationship('Customer')

    def __init__(self, *args, **kwargs):
        super(Entitlement, self).__init__(*args, **kwargs)

        # pylint: disable=no-member
        _id = (int)(uuid4().int / 2**97)

        if db.session.query(Entitlement).get(_id) is not None:
            while db.session.query(Entitlement).get(_id) is not None:
                # pylint: disable=no-member
                _id = (int)(uuid4().int / 2**97)

        self._id = _id
