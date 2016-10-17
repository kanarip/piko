from piko.db import db

class OAuth2Grant(db.Model):
    __tablename__ = 'oauth2_grant'

    id = db.Column(db.Integer, primary_key=True)

    account_id = db.Column(
            db.Integer, db.ForeignKey('account.id', ondelete='CASCADE')
        )

    account = db.relationship('Account')

    client_id = db.Column(
            db.String(40), db.ForeignKey('oauth2_client.id'),
            nullable=False,
        )

    client = db.relationship('OAuth2Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    _scopes = db.Column(db.Text)

    def delete(self):
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
        if self._scopes:
            return self._scopes.split()
        return []
