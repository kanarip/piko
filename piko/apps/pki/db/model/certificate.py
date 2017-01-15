import datetime

from OpenSSL import crypto

from piko.db import db

class Certificate(db.Model):
    """
        A client SSL Certificate
    """
    __tablename__ = 'pki_certificate'

    id = db.Column(db.Integer, primary_key=True)

    cn = db.Column(db.String(36), nullable=False, index=True)

    certificate = db.Column(db.Text, nullable=False)
    private_key = db.Column(db.Text, nullable=False)

    not_before = db.Column(db.DateTime, nullable=True)
    not_after = db.Column(db.DateTime, nullable=True)

    def __init__(self, *args, **kwargs):
        super(Certificate, self).__init__(*args, **kwargs)

        cert = crypto.load_certificate(
            crypto.FILETYPE_PEM,
            kwargs['certificate']
        )

        self.not_before = datetime.datetime.strptime(
            cert.get_notBefore(),
            '%Y%m%d%H%M%SZ'
        )

        self.not_after = datetime.datetime.strptime(
            cert.get_notAfter(),
            '%Y%m%d%H%M%SZ'
        )
