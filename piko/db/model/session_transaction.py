"""
    .. TODO:: A module docstring.
"""
from piko.db import db
from piko.utils import generate_hex_id as generate_id


# pylint: disable=too-few-public-methods
class SessionTransaction(db.Model):
    """
        A session-specific transaction.
    """
    __tablename__ = "session_transaction"

    uuid = db.Column(db.String(32), primary_key=True)

    session_id = db.Column(
        db.String(32),
        db.ForeignKey('session.uuid', ondelete="CASCADE"),
        nullable=False
    )

    transaction_id = db.Column(db.String(32), nullable=False)

    task_id = db.Column(db.String(64), nullable=True)

    session = db.relationship('Session', backref='transactions')

    def __init__(self, *args, **kwargs):
        super(SessionTransaction, self).__init__(*args, **kwargs)

        query = db.session.query

        if 'uuid' in kwargs:
            uuid = kwargs['uuid']
        else:
            uuid = generate_id()

        while query(SessionTransaction).get(uuid) is not None:
            uuid = generate_id()

        self.uuid = uuid

        if 'transaction_id' in kwargs:
            transaction_id = kwargs['transaction_id']
        else:
            transaction_id = generate_id()

        while query(SessionTransaction).filter_by(
                transaction_id=transaction_id
            ).first() is not None:

            transaction_id = generate_id()

        self.transaction_id = transaction_id
