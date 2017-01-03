from sqlalchemy.ext.hybrid import hybrid_property

from piko.db import db

from piko.bcrypt import check_password_hash
from piko.bcrypt import generate_password_hash

from .otp import *

class Person(db.Model):
    """
        An abstract, digital representation of a human being.
    """
    __tablename__ = 'person'

    #: A unique integer ID.
    id = db.Column(db.Integer, primary_key=True)

    #: The name for this account.
    _name = db.Column(db.String(255), nullable=False)

    #: This should be considered a token as well, but is most commonly recognized
    #: as the first token.
    password_hash = db.Column(db.String(128))

    #: Fast preference setting.
    locale = db.Column(db.String(64), default='en')

    #: Fast preference setting.
    timezone = db.Column(db.String(64), default='UTC')

    #: Groups this person is a member of.
    groups = db.relationship(
            'Group',
            secondary="person_groups",
            cascade="delete"
        )

    def __init__(self, *args, **kwargs):
        super(Person, self).__init__(*args, **kwargs)

        _id = (int)(uuid.uuid4().int / 2**97)

        if db.session.query(Person).get(_id) is not None:
            while db.session.query(Person).get(_id) is not None:
                _id = (int)(uuid.uuid4().int / 2**97)

        self.id = _id

    @hybrid_property
    def accounts(self):
        """
            List of accounts associated with this Person.
        """
        from .account import Account

        return self._accounts().all()

    @hybrid_property
    def group_accounts(self):
        """
            List of Accounts associated with Groups associated with
            this Person.
        """
        from .account import Account

        return db.session.query(Account).filter(Account.group_id.in__([x.id for x in self.groups])).all()

    @property
    def password(self):
        raise AttributeError("password cannot be read")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

        change = Change(
                self.__class__.__name__,
                self.id,
                '****',
                '****'
            )

        db.session.add(change)

        self.modified = datetime.datetime.utcnow()

    @hybrid_property
    def second_factor(self):
        """
            The second factor for this account, if any.
        """
        if len([x for x in self.second_factors if x.confirmed]) > 0:
            return self.second_factors[0]

        return False

    @hybrid_property
    def second_factors(self):
        factors = []
        factors.extend(db.session.query(HOTPToken).filter_by(person_id=self.id,confirmed=True).all())
        factors.extend(db.session.query(TANToken).filter_by(person_id=self.id,confirmed=True).all())
        factors.extend(db.session.query(TOTPToken).filter_by(person_id=self.id,confirmed=True).all())
        return factors

    def verify_password(self, password, transaction=None):
        """
            Verify the password.
        """
        if transaction is None:
            result = check_password_hash(self.password_hash, password)
            db.session.add(AccountLogin(account_id=self.id, success=result))
            db.session.commit()
            return result

        else:
            task = check_password_hash.delay(self.password_hash, password)
            transaction.task_id = task.id
            db.session.commit()
            return task.id

    def _accounts(self):
        """
            Return the Query object for Accounts associated with this
            Person.
        """
        from .account import Account

        return db.session.query(Account).filter_by(person_id=self.id)

