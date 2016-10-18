from piko.db import db

class Product(db.Model):
    """
        A product released.
    """
    __tablename__ = 'candlepin_product'

    id = db.Column(db.Integer, primary_key=True)

    key = db.Column(db.String(32), index=True)

    name = db.Column(db.String(128))

    #: End of Sales
    eos = db.Column(db.DateTime)

    #: End of Life
    eol = db.Column(db.DateTime)

    entitlements = db.relationship('Entitlement')
