import datetime

from piko.db import db

class AccountLogin(db.Model):
    __tablename__ = 'account_login'

    id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    success = db.Column(db.Boolean, default=False)
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete="CASCADE"))

    account = db.relationship('Account')
