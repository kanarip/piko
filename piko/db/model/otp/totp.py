import datetime
import otpauth
import urllib
import uuid

from piko.db import db

from .token import OTPToken

class TOTPToken(OTPToken, db.Model):
    __tablename__ = 'otp_token_totp'

    secret = db.Column(db.String(16), nullable=False)

    #: The timestamp the challenge as issued. Relevant primarily for TOTP.
    issued = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    #: The timestamp the last (valid) TOTP as used.
    used = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __init__(self, *args, **kwargs):
        super(TOTPToken, self).__init__(*args, **kwargs)

        _id = (int)(uuid.uuid4().int / 2**96)

        if not db.session.query(TOTPToken).get(_id) == None:
            while len(db.session.query(TOTPToken).get(_id)) > 0:
                _id = (int)(uuid.uuid4().int / 2**96)

        self.id = _id

    def validate_token(self, token):
        auth = otpauth.OtpAuth(self.secret)
        return auth.valid_totp(token)

    def token_config_uri(self, name):
        auth = otpauth.OtpAuth(self.secret)
        result = auth.to_uri('totp', '%s:%s' % (urllib.quote(self.name),urllib.quote(name)), urllib.quote('Kolab Now'))
        return result
