"""
    A grant.
"""
from piko.db import db

class OAuth2Grant(db.Model):
    """
        A grant.
    """
    __tablename__ = 'oauth2_grant'

    uuid = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(
        db.Integer, db.ForeignKey('account.uuid', ondelete='CASCADE')
    )

    account = db.relationship('Account')

    client_id = db.Column(
        db.String(40), db.ForeignKey('oauth2_client.uuid'),
        nullable=False
    )

    client = db.relationship('OAuth2Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
        """
            .. TODO:: A docstring.
        """
        db.session.delete(self)
        db.session.commit()
        return self

    @property
    def user(self):
        """
            A proxy to ``self.account``
        """
        return self.account

    @property
    def scopes(self):
        """
            .. TODO:: A docstring.
        """
        if self._scopes:
            return self._scopes.split()
        return []
