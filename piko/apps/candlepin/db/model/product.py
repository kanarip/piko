from piko.db import db

class Product(db.Model):
    """
        A product released.
    """
    __tablename__ = 'candlepin_product'

    #: The unique ID for this product
    id = db.Column(db.Integer, primary_key=True)

    #: A machine readable key
    key = db.Column(db.String(32), index=True)

    #: A human readable name or title
    name = db.Column(db.String(128))

    #: The ID of a parent product ID, such as an additional opt-in repository
    #: with feature-specific packages that requires the base repository to be
    #: available as well.
    parent_id = db.Column(
            db.Integer,
            db.ForeignKey('candlepin_product.id', ondelete='CASCADE'),
            nullable=True
        )

    #: End of Sales
    eos = db.Column(db.DateTime)

    #: End of Life
    eol = db.Column(db.DateTime)

    #: Proxy to the entitlements associated with this product.
    entitlements = db.relationship('Entitlement')
