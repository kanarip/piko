"""
    Database model definition for a domain (name space).
"""
from piko.db import db

from piko.utils import generate_int_id as generate_id

# pylint: disable=bad-whitespace

# Who knows?
STATE_UNKNOWN   = 1 << 0
# New, whatever that means.
STATE_NEW       = 1 << 1
# External, meaning its not ours and not the user's either.
STATE_EXTERNAL  = 1 << 2
# Ownership confirmed.
STATE_CONFIRMED = 1 << 3
# Somehow make allowing traffic true and from to be secure only.
STATE_SECURE    = 1 << 4
# Whether or not the domain (name space) is hosted with us.
STATE_HOSTED    = 1 << 5
# Whether or not the domain (name space) got suspended.
STATE_SUSPENDED = 1 << 6

# TODO: Consider sub-domain name spaces not too disconnected from parent domain
#       name spaces.

class Domain(db.Model):
    """
        A domain.
    """

    __tablename__ = "asp_domain"

    uuid = db.Column(db.Integer, primary_key=True)

    #: The namespace for this domain.
    namespace = db.Column(db.String(256), index=True, nullable=False)

    #: The state representation of the domain
    state = db.Column(db.Integer, default=False, nullable=False)

    #: Parent ID
    parent_id = db.Column(
        db.Integer,
        db.ForeignKey('asp_domain.uuid', ondelete='CASCADE'),
        nullable=True
    )

    parent = db.relationship('Domain')

    def __init__(self, *args, **kwargs):
        super(Domain, self).__init__(*args, **kwargs)

        uuid = generate_id()

        if db.session.query(Domain).get(uuid) is not None:
            while db.session.query(Domain).get(uuid) is not None:
                uuid = generate_id()

        self.uuid = uuid

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
        return db.session.query(Domain).filter_by(parent_id=self.uuid).all()
