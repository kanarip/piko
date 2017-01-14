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

    _id = db.Column(db.Integer, primary_key=True)

    timestamp = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    success = db.Column(db.Boolean, default=False)

    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account._id', ondelete="CASCADE")
    )

    account = db.relationship('Account')

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
