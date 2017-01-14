"""
    Database model definition for a domain (name space).
"""

from piko.db import db

class Domain(db.Model):
    """
        A domain.
    """

    __tablename__ = "asp_domain"

    _id = db.Column(db.Integer, primary_key=True)

    #: The namespace for this domain.
    namespace = db.Column(db.String(256), index=True, nullable=False)

    #: Is this domain hosted with us?
    hosted = db.Column(db.Boolean, default=False, nullable=False)

    #: Is the ownership of this domain confirmed?
    hosted_verified = db.Column(db.Boolean, default=False, nullable=False)

    #: Parent ID
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('asp_domain._id', ondelete='CASCADE'),
        nullable=True
    )

    parent = db.relationship('Domain')

    def parentdomain(self):
        """
            Return the parent domain name space as a string, or None.
        """
        if self.parent_id is not None:
            return self.parent.namespace
        else:
            return None

    def subdomains(self):
        """
            Return a list of subdomains.
        """
        return db.session.query(Domain).filter_by(parent_id=self._id).all()
