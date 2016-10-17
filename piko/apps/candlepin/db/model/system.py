from uuid import uuid4

from piko.db import db

class System(db.Model):
    __tablename__ = 'candlepin_system'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), index=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('candlepin_customer.id', ondelete='CASCADE'))

    customer = db.relationship('Customer')

    def __init__(self, *args, **kwargs):
        super(System, self).__init__(*args, **kwargs)

        _id = (int)(uuid4().int / 2**97)

        if db.session.query(System).get(_id) is not None:
            while db.session.query(System).get(_id) is not None:
                _id = (int)(uuid4().int / 2**97)

        self.id = _id

        uuid = uuid4().__str__()

        if db.session.query(System).filter_by(uuid=uuid).first() is not None:
            while db.session.query(System).filter_by(uuid=uuid).first() is not None:
                uuid = uuid4().__str__()

        self.uuid = uuid
