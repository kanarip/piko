from piko.db import db

class Entitlement(db.Model):
    __tablename__ = 'candlepin_entitlement'

    id = db.Column(db.Integer, primary_key=True)

    system_id = db.Column(db.Integer, db.ForeignKey('candlepin_system.id'), nullable=True)

    product_id = db.Column(db.Integer, db.ForeignKey('candlepin_product.id'), nullable=True)
