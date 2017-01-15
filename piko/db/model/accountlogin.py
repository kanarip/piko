"""
    .. TODO:: A module docstring.
"""
import datetime

from piko.db import db


class AccountLogin(db.Model):
    """
        .. TODO:: A class docstring.
    """
    __tablename__ = 'account_login'

    uuid = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    success = db.Column(db.Boolean, default=False)

    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account.uuid', ondelete="CASCADE"),
        nullable=True
    )

    account = db.relationship('Account')

    person_id = db.Column(
        db.Integer,
        db.ForeignKey('person.uuid', ondelete="CASCADE"),
        nullable=True
    )

    person = db.relationship('Person')

    def log_success(self, account_id):
        """
            Log a successful login.
        """
        pass

    def log_failure(self, account_id):
        """
            Log a failed login attempt.
        """
        pass
