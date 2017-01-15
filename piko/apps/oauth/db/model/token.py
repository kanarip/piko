"""
    Database definition for an OAuth2 Token
"""

from piko.db import db

class OAuth2Token(db.Model):
    """
        An OAuth2 Token
    """
    __tablename__ = 'oauth2_token'

    uuid = db.Column(db.Integer, autoincrement=True, primary_key=True)

    #: Client ID, links to :py:attr:`piko.apps.oauth.db.model.Client.id`
    client_id = db.Column(
        db.String(40), db.ForeignKey('oauth2_client.uuid'),
        nullable=False
    )

    client = db.relationship('OAuth2Client')

    account_id = db.Column(
        db.Integer, db.ForeignKey('account.uuid')
    )

    account = db.relationship('Account')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def delete(self):
        """
            Remove this token.
        """

        db.session.delete(self)
        db.session.commit()

        return self

    @property
    def scopes(self):
        """
            Return the scopes this token is valid for.
        """
        if self._scopes:
            return self._scopes.split()

        return []
