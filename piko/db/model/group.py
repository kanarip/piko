"""
    .. TODO:: A module docstring.
"""
from piko.db import db
from piko.utils import generate_int_id as generate_id


# pylint: disable=too-few-public-methods
class Group(db.Model):
    """
        An abstract, digital representation of a group of
        :py:class:`Accounts <piko.db.model.Account>` or
        :py:class:`Persons <piko.db.model.Persons>`.

        A group can be a simple collection of Accounts, such that
        a family of "John" and "Jane" can be grouped as the
        "Doe Family".

        Both "John" and "Jane" would have accounts.

    """
    __tablename__ = 'group'

    #: An automatically generated unique integer ID
    uuid = db.Column(db.Integer, primary_key=True)

    _name = db.Column(db.String(255), nullable=False)

    #: List of :py:class:`piko.db.model.Account` records associated
    #: with this :py:class:`Group`.
    accounts = db.relationship('Account')

    #: List of :py:class:`piko.db.model.Person` records associated
    #: with this :py:class:`Group`.
    persons = db.relationship(
        'Person',
        secondary="person_groups",
        cascade="delete"
    )

    def __init__(self, *args, **kwargs):
        """
            When a group is created, assign it a unique integer ID.
        """
        super(Group, self).__init__(*args, **kwargs)

        uuid = generate_id()

        if db.session.query(Group).get(uuid) is not None:
            while db.session.query(Group).get(uuid) is not None:
                uuid = generate_id()

        self.uuid = uuid

    @property
    def name(self):
        """
            A display name such as 'Doe Family' or 'Example, Inc.'.
        """

        return self._name

    @name.setter
    def name(self, value):
        self._name = value
