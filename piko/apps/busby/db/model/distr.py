from piko.db import db

class Distribution(db.Model):
    __tablename__ = 'busby_distr'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), nullable=False, index=True)

