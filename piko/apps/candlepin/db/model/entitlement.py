from piko.db import db

class Entitlement(db.Model):
    __tablename__ = 'candlepin_entitlement'

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(db.Integer, db.ForeignKey('candlepin_customer.id', ondelete='CASCADE'), nullable=False)

    product_id = db.Column(db.Integer, db.ForeignKey('candlepin_product.id', ondelete='CASCADE'), nullable=True)

    quantity = db.Column(db.Integer, default=-1)

    customer = db.relationship('Customer')
