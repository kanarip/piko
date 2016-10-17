from uuid import uuid4

from piko.db import db

class System(db.Model):
    __tablename__ = 'candlepin_system'

    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), index=True)

    def __init__(self, *args, **kwargs):
        super(System, self).__init__(*args, **kwargs)

        _id = (int)(uuid4().int / 2**96)

        while len(db.session.query(System).get(_id)) > 0:
            _id = (int)(uuid4().int / 2**96)

        self.id = _id

        uuid = uuid4().__str__()

        while len(db.session.query(System).filter_by(uuid=uuid)) > 0:
            uuid = uuid4().__str__()

        self.uuid = uuid
