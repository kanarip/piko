from piko.db import db

class Customer(db.Model):
    """
        A product released.
    """
    __tablename__ = 'candlepin_customer'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(128))

    #: Created
    created = db.Column(db.DateTime)

    #: Modified
    modified = db.Column(db.DateTime)

    def __init__(self, *args, **kwargs):
        super(Customer, self).__init__(*args, **kwargs)

        _id = (int)(uuid4().int / 2**96)

        if db.session.query(Customer).get(_id) is not None:
            while db.session.query(Customer).get(_id) is not None:
                _id = (int)(uuid4().int / 2**96)

        self.id = _id
