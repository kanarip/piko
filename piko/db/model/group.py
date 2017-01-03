from piko.db import db

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
    id = db.Column(db.Integer, primary_key=True)

    _name = db.Column(db.String(255), nullable=False)

    #: List of :py:class:`piko.db.model.Account` records associated
    #: with this :py:class:`Group`.
    accounts = db.relationship('Account')

    #: List of :py:class:`piko.db.model.Person` records associated
    #: with this :py:class:`Group`.
    persons = db.relationship(
            'Person',
            secondary = "person_groups",
            cascade = "delete"
        )

    def __init__(self, *args, **kwargs):
        """
            When a group is created, assign it a unique integer ID.
        """
        super(Group, self).__init__(*args, **kwargs)

        _id = (int)(uuid.uuid4().int / 2**97)

        if db.session.query(Group).get(_id) is not None:
            while db.session.query(Group).get(_id) is not None:
                _id = (int)(uuid.uuid4().int / 2**97)

        self.id = _id

    @property
    def name(self):
        """
            A display name such as 'Doe Family' or 'Example, Inc.'.
        """

        return self._name

    @name.setter
    def name(self, value):
        self._name = value

