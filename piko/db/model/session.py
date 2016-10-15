import datetime
import os
import uuid

from piko.db import db

class Session(db.Model):
    """
        The basis of an account.

        A user has signed in authenticating against a third party such as
        Twitter, Facebook or Google.
    """
    __tablename__ = "session"

    #: The session UUID as part of the visitor's cookie. Note this is
    #: the hexadecimal version of a uuid.uuid4().
    id = db.Column(db.String(32), primary_key=True)

    #: In case the user is authenticated, this points to the associated account.
    account_id = db.Column(db.Integer, db.ForeignKey('account.id', ondelete="CASCADE"), nullable=True)

    redirect = db.Column(db.String(256))

    #: The expiry date and time
    expires = db.Column(db.DateTime, default=None)

    def reset_transactions(self):
        for t in self.transactions:
            db.session.delete(t)

        db.session.commit()
