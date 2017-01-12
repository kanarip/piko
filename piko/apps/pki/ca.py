import os

from OpenSSL import crypto

def sign_cert(cert):
    base_path = os.path.join(
            os.path.dirname(__file__),
            '..', # up from pki/.
            '..', # up from apps/.
            '..', # up from piko/.
            'tmp'
        )

    ca_path = os.path.join(base_path, 'ca')

    passphrase = open(
            os.path.join(ca_path, 'mirror_ca.pass'),
            'r'
        ).read().strip()

    ca_key = crypto.load_privatekey(
            crypto.FILETYPE_PEM,
            open(os.path.join(ca_path, 'mirror_ca.key'), 'r').read(),
            passphrase = passphrase
        )

    ca_cert = crypto.load_certificate(
            crypto.FILETYPE_PEM,
            open(os.path.join(ca_path, 'mirror_ca.cert'), 'r').read()
        )

    ca_subject = ca_cert.get_subject()
    cert_issuer = cert.get_issuer()

    dn_attrs = [
            'C',
            'ST',
            'L',
            'O',
            'OU',
            'CN',
            'emailAddress'
        ]

    for dn_attr in dn_attrs:
        if hasattr(ca_subject, dn_attr):
            if getattr(ca_subject, dn_attr) is not None:
                setattr(cert_issuer, dn_attr, getattr(ca_subject, dn_attr))

    cert.add_extensions(
            [
                    crypto.X509Extension(
                            "subjectKeyIdentifier",
                            False,
                            "hash",
                            subject = cert
                        ),

                    crypto.X509Extension(
                            "basicConstraints",
                            True,
                            "CA:FALSE"
                        ),

                    #crypto.X509Extension(
                    #        "keyUsage",
                    #        False,
                    #        "digitalSignature"
                    #    ),

                    crypto.X509Extension(
                            "extendedKeyUsage",
                            False,
                    #        "clientAuth,serverAuth"
                            "clientAuth"
                        ),

                    crypto.X509Extension(
                            "authorityKeyIdentifier",
                            False,
                            "keyid:always",
                            issuer = ca_cert
                        )
                ]
        )

    cert.sign(ca_key, "md5")
    cert.sign(ca_key, "sha1")
    cert.sign(ca_key, "sha256")
    cert.sign(ca_key, "sha512")

    return cert
