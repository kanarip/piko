"""
    .. TODO:: A module docstring.
"""
from uuid import uuid4

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
    uuid = db.Column(db.String(32), primary_key=True)

    #: The account ID stored here should be a very temporary placeholder
    #: for getting to an actual person logging in -- using an account.
    account_id = db.Column(
        db.Integer,
        db.ForeignKey('account._id', ondelete="CASCADE"),
        nullable=True
    )

    #: In case the user is authenticated, this points to the associated
    #: account.
    person_id = db.Column(
        db.Integer,
        db.ForeignKey('person._id', ondelete="CASCADE"),
        nullable=True
    )

    redirect = db.Column(db.String(256))

    #: The expiry date and time
    expires = db.Column(db.DateTime, default=None)

    def associate_account_id(self, account_id):
        """
            Associate this session with an account.
        """
        assert self.account_id is None
        assert self.person_id is None

        self.account_id = account_id

        db.session.commit()

    def associate_person_id(self, person_id):
        """
            Associate this session with a person.
        """
        assert self.account_id is not None
        assert self.person_id is None

        self.person_id = person_id
        self.account_id = None

        db.session.commit()

    def reset_transactions(self):
        """
            Reset the transations for this session.
        """
        for transaction in self.transactions:
            db.session.delete(transaction)

        db.session.commit()

    def __init__(self, *args, **kwargs):
        super(Session, self).__init__(*args, **kwargs)

        uuid = uuid4().__str__()

        query = db.session.query

        if query(Session).filter_by(uuid=uuid).first() is not None:
            while query(Session).filter_by(uuid=uuid).first() is not None:
                uuid = uuid4().__str__()

        self.uuid = uuid
