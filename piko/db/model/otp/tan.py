import datetime
import uuid

from piko.db import db

from .token import OTPToken

class TANToken(OTPToken, db.Model):
    """
        Temporary Authorization Number (TAN)
    """

    __tablename__ = 'otp_token_tan'

    #: The timestamp the challenge as issued. Relevant primarily for TOTP.
    issued = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    phone_number = db.Column(db.Integer, nullable=False)

    tan = db.Column(db.Integer, nullable=False, default=-1)

    def __init__(self, *args, **kwargs):
        super(TOTPToken, self).__init__(*args, **kwargs)

        _id = (int)(uuid.uuid4().int / 2**96)

        if not db.session.query(TOTPToken).get(_id) == None:
            while len(db.session.query(TOTPToken).get(_id)) > 0:
                _id = (int)(uuid.uuid4().int / 2**96)

        self.id = _id

