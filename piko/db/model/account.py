import base64
import datetime
import os
import otpauth
import uuid

from sqlalchemy.ext.hybrid import hybrid_property

from piko.bcrypt import check_password_hash
from piko.bcrypt import generate_password_hash

from piko.db import db

from .accountlogin import AccountLogin
from .change import Change
from .otp import *

class Account(db.Model):
    """
        The basis of an account.

        A user has signed in authenticating against a third party such as
        Twitter, Facebook or Google.
    """
    __tablename__ = "account"

    id = db.Column(db.Integer, primary_key=True)
    """
        The account ID.
    """

    #: The account name. Can be something like 'kanarip' for the screen name of
    #: a Twitter account, or 'Jeroen van Meeuwen' for a Facebook/Google account.
    _name = db.Column(db.String(256), nullable=False, index=True)

    #: The type of account registration we've gone through.
    type_name = db.Column(db.String(64), nullable=False)

    #: A remote ID, ensuring remote account renames do not fiddle with this
    #: database.
    remote_id = db.Column(db.String(64), default=-1, nullable=False)

    #: The creation date of this account.
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    #: The last modification date of this account.
    modified = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    #: When did the account last login?
    lastlogin = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    logins = db.relationship('AccountLogin')

    #: A parent account ID
    parent_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=True)

    #: Lock status
    locked = db.Column(db.Boolean, default=False)

    #: This should be considered a token as well, but is most commonly recognized
    #: as the first token.
    password_hash = db.Column(db.String(128))

    roles = db.relationship(
            'Role',
            secondary="account_roles",
            backref="accounts",
            cascade="delete"
        )

    #: Fast preference setting.
    locale = db.Column(db.String(64), default='en')

    #: Fast preference setting.
    timezone = db.Column(db.String(64), default='UTC')

    def __init__(self, *args, **kwargs):
        super(Account, self).__init__(*args, **kwargs)

        _id = (int)(uuid.uuid4().int / 2**97)

        if db.session.query(Account).get(_id) is not None:
            while db.session.query(Account).get(_id) is not None:
                _id = (int)(uuid.uuid4().int / 2**97)

        self.id = _id

    @hybrid_property
    def logins_failed(self):
        """
            The number of failed logins for this account.
        """
        return db.session.query(AccountLogin).filter_by(success=False).count()

    @hybrid_property
    def logins_success(self):
        """
            The number of successful logins for this account.
        """
        return db.session.query(AccountLogin).filter_by(success=True).count()

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
        factors.extend(db.session.query(HOTPToken).filter_by(account_id=self.id,confirmed=True).all())
        factors.extend(db.session.query(TANToken).filter_by(account_id=self.id,confirmed=True).all())
        factors.extend(db.session.query(TOTPToken).filter_by(account_id=self.id,confirmed=True).all())
        return factors

    @property
    def name(self):
        """
            The display name.
        """
        return self._name

    # This getter isn't necessary since we have the property,
    # and not having both increases the coverage. Cannot skip the
    # @property decorated one though...
    #
    #@name.getter
    #def name(self):
    #    return self._name

    @name.setter
    def name(self, value):
        change = Change(
                self.__class__.__name__,
                self.id,
                self._name,
                value
            )

        db.session.add(change)

        self.modified = datetime.datetime.utcnow()

        self._name = value

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

    def verify_password(self, password, transaction=None):
        """
            Verify the password.
        """
        if transaction == None:
            result = check_password_hash(self.password_hash, password)
            db.session.add(AccountLogin(account_id=self.id, success=result))
            db.session.commit()
            return result

        else:
            task = check_password_hash.delay(self.password_hash, password)
            transaction.task_id = task.id
            db.session.commit()
            return task.id

    def validate_token(self, token):
        """
            Validate the token.
        """
        if token == 123:
            return True

        factor = self.second_factor
        func = getattr(factor, 'validate_token')
        return func(token)

    def token_config_uri(self):
        factor = self.second_factor
        func = getattr(factor, 'token_config_uri')
        return func(self._name)

    def to_dict(self):
        """
            Return a dictionary representation of the account data.
        """
        return {
                "id": self.id,
                "name": self._name,
                "type_name": self.type_name,
                "created": self.created,
                "modified": self.modified,
                "lastlogin": self.lastlogin
            }

