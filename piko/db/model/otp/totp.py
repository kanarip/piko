"""
    piko.db.model.OTPToken
    ======================

    A time-based OTP token.
"""
import datetime
import urllib

import otpauth

from piko.db import db
from piko.utils import generate_int_id as generate_id

from .token import OTPToken

class TOTPToken(OTPToken, db.Model):
    """
        A time-based OTP token.
    """
    __tablename__ = 'otp_token_totp'

    secret = db.Column(db.String(16), nullable=False)

    #: The timestamp the challenge as issued. Relevant primarily for TOTP.
    issued = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    #: The timestamp the last (valid) TOTP as used.
    used = db.Column(
        db.DateTime,
        default=datetime.datetime.utcnow,
        nullable=False
    )

    def __init__(self, *args, **kwargs):
        super(TOTPToken, self).__init__(*args, **kwargs)

        uuid = generate_id()

        if db.session.query(TOTPToken).get(uuid) is not None:
            while db.session.query(TOTPToken).get(uuid) is not None:
                uuid = generate_id()

        self.uuid = uuid

    def validate_token(self, token):
        """
            Validate the token.
        """
        auth = otpauth.OtpAuth(self.secret)
        result = auth.valid_totp(token)

        if result:
            self.used = datetime.datetime.utcnow()
            db.session.commit()

        return result

    def token_config_uri(self, name):
        """
            Get the token configuration URL.
        """
        auth = otpauth.OtpAuth(self.secret)

        result = auth.to_uri(
            'totp',
            '%s:%s' % (urllib.quote(self.name), urllib.quote(name)),
            urllib.quote('piko')
        )

        return result
