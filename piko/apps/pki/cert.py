import datetime
import os
import uuid

from OpenSSL import crypto

from piko.db import db
from piko.apps.pki.db.model import Certificate

base_path = os.path.join(
        os.path.dirname(__file__),
        '..', # up from pki/.
        '..', # up from apps/.
        '..', # up from piko/.
        'tmp'
    )

cert_path = os.path.join(base_path, 'certs')

class Cert(object):
    def __init__(self, system_uuid, *args, **kw):
        self.system_uuid = system_uuid

    def generate_cert(self):
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 4096)

        cert = crypto.X509()

        subject = cert.get_subject()
        subject.C = "CH"
        subject.ST = "Zurich"
        subject.O = "Kolab Systems AG"
        subject.OU = "Product Sales"
        subject.CN = self.system_uuid
        subject.emailAddress = "support@kolabsys.com"

        cert.set_pubkey(key)
        cert.set_version(2)

        start = datetime.datetime.utcnow()
        end = start + datetime.timedelta(days=365)

        cert.set_notBefore(start.strftime("%Y%m%d%H%M%SZ"))
        cert.set_notAfter(end.strftime("%Y%m%d%H%M%SZ"))

        serial_number = uuid.uuid4().int
        cert.set_serial_number(serial_number)

        from .ca import sign_cert

        cert = sign_cert(cert)

        pem_cert = crypto.dump_certificate(crypto.FILETYPE_TEXT, cert)
        pem_cert += crypto.dump_certificate(crypto.FILETYPE_PEM, cert)

        pem_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
        pem = pem_cert + pem_key

        pem_path = os.path.join(cert_path, '%s.pem' % (self.system_uuid))

        with open(pem_path, 'w') as f:
            f.write(pem)

        _cert = Certificate(
                cn = self.system_uuid,
                certificate = pem_cert,
                private_key = pem_key
            )

        db.session.add(_cert)

        db.session.commit()

        return (cert, key)


