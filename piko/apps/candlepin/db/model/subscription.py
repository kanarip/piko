from piko.db import db

class Subscription(db.Model):
    __tablename__ = 'candlepin_subscription'

    id = db.Column(db.Integer, primary_key=True)

    entitlement_id = db.Column(db.Integer, db.ForeignKey('candlepin_entitlement.id'), nullable=False)
