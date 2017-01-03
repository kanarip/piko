import sys
import unittest

sys.path.insert(0, '.')

from piko.db import db
from piko.db.model import Person

class TestPerson(unittest.TestCase):
    def test_000_john(self):
        #: Fixtures say this is John
        person = db.session.query(Person).get(1)

        assert person

        # John has a personal and a professional email account.
        assert len(person.accounts)

        # John's a member of the "Doe Family" and "Example, Inc." groups.
        assert len(person.groups)

        # John's employer has a twitter account
        assert len(person.group_accounts)
