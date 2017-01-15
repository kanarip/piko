from piko.db import db

class OAuth2Client(db.Model):
    __tablename__ = 'oauth2_client'

    #: The Client ID. Distributed to application owners
    uuid = db.Column(db.String(36), primary_key=True)

    #: A human readable name, not required.
    name = db.Column(db.String(40))

    #: A human readable description, not required.
    description = db.Column(db.String(400))

    #: The secret the client application needs to use.
    secret = db.Column(db.String(55), unique=True, index=True, nullable=False)

    confidential = db.Column(db.Boolean, default=True)

    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)

    @property
    def client_id(self):
        return self.uuid

    @property
    def client_secret(self):
        return self.secret

    @property
    def client_type(self):
        if self.confidential:
            return 'confidential'

        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            result = self._redirect_uris.split()
        else:
            result = []

        print "OAuth2Client.redirect_uris():", result

        return result

    @property
    def default_redirect_uri(self):
        if self._redirect_uris:
            return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()

        return []
