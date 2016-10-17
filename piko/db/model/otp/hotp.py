import otpauth
import urllib
import uuid

from piko.db import db

from .token import OTPToken

class HOTPToken(OTPToken, db.Model):
    __tablename__ = 'otp_token_hotp'

    secret = db.Column(db.String(16), nullable=False)

    #: The counter
    counter = db.Column(db.Integer, default=1, nullable=False)

    def __init__(self, *args, **kwargs):
        super(HOTPToken, self).__init__(*args, **kwargs)

        _id = (int)(uuid.uuid4().int / 2**96)

        if db.session.query(HOTPToken).get(_id) is not None:
            while db.session.query(HOTPToken).get(_id) is not None:
                _id = (int)(uuid.uuid4().int / 2**96)

        self.id = _id

    def validate_token(self, token):
        auth = otpauth.OtpAuth(self.secret)
        result = auth.valid_hotp(token, last=self.counter)
        if not result:
            return False

        self.counter = result
        db.session.commit()
        return True

    def token_config_uri(self, name):
        auth = otpauth.OtpAuth(self.secret)
        result = auth.to_uri('hotp', '%s:%s' % (urllib.quote(self.name),urllib.quote(name)), urllib.quote('Kolab Now'), counter=self.counter)
        return result
