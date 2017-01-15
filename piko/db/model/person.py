"""
    .. TODO:: A module docstring.
"""
from sqlalchemy.ext.hybrid import hybrid_property

from piko.db import db
from piko.utils import generate_int_id as generate_id

from piko.bcrypt import check_password_hash
from piko.bcrypt import generate_password_hash

from .change import Change
from .otp import HOTPToken
from .otp import TOTPToken
from .otp import TANToken


class Person(db.Model):
    """
        An abstract, digital representation of a human being.
    """
    __tablename__ = 'person'

    #: A unique integer ID.
    uuid = db.Column(db.Integer, primary_key=True)

    #: The name for this person.
    name = db.Column(db.String(255), nullable=False)

    #: This should be considered a token as well, but is most commonly
    #: recognized as the first token.
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

        if 'uuid' in kwargs:
            uuid = kwargs['uuid']
        else:
            uuid = generate_id()

        while db.session.query(Person).get(uuid) is not None:
            uuid = generate_id()

        self.uuid = uuid

    @hybrid_property
    def accounts(self):
        """
            List of accounts associated with this Person.
        """
        return self._accounts().all()

    @hybrid_property
    def group_accounts(self):
        """
            List of Accounts associated with Groups associated with
            this Person.
        """
        groups = []
        for group in self.groups:
            groups.append(group)

        return groups

    @property
    def password(self):
        """
            Proxy getting the password.
        """
        raise AttributeError("password cannot be read")

    @password.setter
    def password(self, password):
        """
            Set a new passord.
        """
        # pylint: disable=no-value-for-parameter
        self.password_hash = generate_password_hash(password)

        change = Change(
            object_name=self.__class__.__name__,
            object_id=self.uuid,
            attribute_name='password',
            value_from='****',
            value_to='****'
        )

        db.session.add(change)

    @hybrid_property
    def second_factor(self):
        """
            The second factor for this account, if any.
        """
        # pylint: disable=not-an-iterable
        if len([x for x in self.second_factors if x.confirmed]) > 0:
            # pylint: disable=unsubscriptable-object
            return self.second_factors[0]

        return False

    @hybrid_property
    def second_factors(self):
        """
            Return a list of second factors.
        """
        factors = []

        factors.extend(
            db.session.query(HOTPToken).filter_by(
                person_id=self.uuid,
                confirmed=True
            ).all()
        )

        factors.extend(
            db.session.query(TANToken).filter_by(
                person_id=self.uuid,
                confirmed=True
            ).all()
        )

        factors.extend(
            db.session.query(TOTPToken).filter_by(
                person_id=self.uuid,
                confirmed=True
            ).all()
        )

        return factors

    def verify_password(self, password, transaction=None):
        """
            Verify the password.
        """
        if transaction is None:
            # pylint: disable=no-value-for-parameter
            result = check_password_hash(self.password_hash, password)

            from .accountlogin import AccountLogin

            db.session.add(AccountLogin(person_id=self.uuid, success=result))
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

        return db.session.query(Account).filter_by(person_id=self.uuid)

    def to_dict(self):
        """
            Return a dictionary presentation of this object.
        """
        groups = self.groups

        group_accounts = []

        for group in groups:
            if len(group.accounts) > 1:
                for account in group.accounts:
                    group_accounts.append(account.name)

        return {
            'locale': self.locale,
            'groups': [x.name for x in self.groups],
            # pylint: disable=not-an-iterable
            'accounts': [x.name for x in self.accounts],
            'group_accounts': group_accounts
        }
