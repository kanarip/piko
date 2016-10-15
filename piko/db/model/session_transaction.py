import datetime
import os
import uuid

from piko.db import db

class SessionTransaction(db.Model):
    """
        A task.
    """
    __tablename__ = "session_transaction"

    id = db.Column(db.Integer, primary_key=True)

    session_id = db.Column(db.String(64), db.ForeignKey('session.id', ondelete="CASCADE"), nullable=False)

    transaction_id = db.Column(db.String(64), nullable=False)

    task_id = db.Column(db.String(64), nullable=True)

    session = db.relationship('Session', backref='transactions')

    def __init__(self, *args, **kwargs):
        super(SessionTransaction, self).__init__(*args, **kwargs)

        self.transaction_id = uuid.uuid4().__str__()
