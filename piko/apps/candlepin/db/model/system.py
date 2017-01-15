"""
    .. TODO:: A module docstring.
"""
from piko.db import db
from piko.utils import generate_uuid


# pylint: disable=too-few-public-methods
class System(db.Model):
    """
        .. TODO:: A class docstring.
    """
    __tablename__ = 'candlepin_system'

    uuid = db.Column(db.String(36), primary_key=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('candlepin_customer.uuid', ondelete='CASCADE')
    )

    customer = db.relationship('Customer')

    def __init__(self, *args, **kwargs):
        super(System, self).__init__(*args, **kwargs)

        uuid = generate_uuid()

        if db.session.query(System).get(uuid) is not None:
            while db.session.query(System).get(uuid) is not None:
                uuid = generate_uuid()

        self.uuid = uuid
