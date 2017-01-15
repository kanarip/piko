"""
    piko.db.model.TANToken
    ======================

    Temp. Authz. Number
"""
import datetime

from piko.db import db
from piko.utils import generate_int_id as generate_id

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
        super(TANToken, self).__init__(*args, **kwargs)

        uuid = generate_id()

        if db.session.query(TANToken).get(uuid) is not None:
            while db.session.query(TANToken).get(uuid) is not None:
                uuid = generate_id()

        self.uuid = uuid
