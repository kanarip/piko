"""
    candlepin.db.model.Customer
    ===========================
"""
from datetime import datetime

from piko.db import db
from piko.utils import generate_int_id as generate_id


# pylint: disable=too-few-public-methods
class Customer(db.Model):
    """
        A customer.
    """
    __tablename__ = 'candlepin_customer'

    #: The unique ID for the customer. Note that this ID cannot be predictable,
    #: and is generated.
    uuid = db.Column(db.Integer, primary_key=True)

    #: A name for the customer. Think along the lines of *Example, Inc.*.
    name = db.Column(db.String(128))

    #: The date and time this customer was created -- GMT.
    created = db.Column(db.DateTime, default=datetime.utcnow)

    modified = db.Column(db.DateTime, default=datetime.utcnow)
    """
        The date and time this customer was modified -- GMT.

        .. NOTE::

            It should probably be linked with a 'whodunnit', and it should
            also be updated (automatically).
    """

    entitlements = db.relationship('Entitlement')

    systems = db.relationship('System')

    def __init__(self, *args, **kwargs):
        """
            Upon creation of the customer entity, ensure that the integer ID
            assigned to it is random as well as unique without trial and error.
        """
        super(Customer, self).__init__(*args, **kwargs)

        uuid = generate_id()

        if db.session.query(Customer).get(uuid) is not None:
            while db.session.query(Customer).get(uuid) is not None:
                uuid = generate_id()

        self.uuid = uuid
