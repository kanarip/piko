from datetime import datetime
from uuid import uuid4

from piko.db import db

class Customer(db.Model):
    """
        A product released.
    """
    __tablename__ = 'candlepin_customer'

    #: The unique ID for the customer. Note that this ID cannot be predictable,
    #: and is generated.
    id = db.Column(db.Integer, primary_key=True)

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

        _id = (int)(uuid4().int / 2**97)

        if db.session.query(Customer).get(_id) is not None:
            while db.session.query(Customer).get(_id) is not None:
                _id = (int)(uuid4().int / 2**97)

        self.id = _id
