"""
    .. TODO:: A module docstring.
"""
from uuid import uuid4

from piko.db import db


# pylint: disable=too-few-public-methods
class System(db.Model):
    """
        .. TODO:: A class docstring.
    """
    __tablename__ = 'candlepin_system'

    #: Unique ID. Separate from the uuid since the uuid may persist
    #: indefinitely.
    _id = db.Column(db.Integer, primary_key=True)

    uuid = db.Column(db.String(36), index=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('candlepin_customer._id', ondelete='CASCADE')
    )

    customer = db.relationship('Customer')

    def __init__(self, *args, **kwargs):
        super(System, self).__init__(*args, **kwargs)

        # pylint: disable=no-member
        _id = (int)(uuid4().int / 2**97)

        if db.session.query(System).get(_id) is not None:
            while db.session.query(System).get(_id) is not None:
                # pylint: disable=no-member
                _id = (int)(uuid4().int / 2**97)

        self._id = _id

        uuid = uuid4().__str__()

        query = db.session.query

        if query(System).filter_by(uuid=uuid).first() is not None:
            while query(System).filter_by(uuid=uuid).first() is not None:
                uuid = uuid4().__str__()

        self.uuid = uuid
