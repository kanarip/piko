"""
    Test :py:class:`piko.db.model.Person`
"""
import unittest

# pylint: disable=wrong-import-position
from piko.db import db
from piko.db.model import Person


class TestPerson(unittest.TestCase):
    """
        Test :py:class:`piko.db.model.Person`
    """
    # pylint: disable=no-self-use
    def test_000_john(self):
        """
            Test operations on fixtures
        """

        #: Fixtures say this is John
        person = db.session.query(Person).get(1)

        assert person

        # John has a personal and a professional email account.
        assert len(person.accounts)

        # John's a member of the "Doe Family" and "Example, Inc." groups.
        assert len(person.groups)

        # John's employer has a twitter account
        assert len(person.group_accounts) == 2

    def test_001_duplicate_uuid(self):
        person = Person(
            uuid=1,
            name='Test 001.001'
        )

        assert person.uuid is not None
        assert person.uuid is not 1

        db.session.add(person)
        db.session.commit()

    def test_002_generate_uuid(self):
        person = Person(
            name='Test 001.002'
        )

        assert person.uuid is not None
        assert person.uuid is not 1

        db.session.add(person)
        db.session.commit()

    def test_003_read_password(self):
        person = Person(
            name='Test 001.003'
        )

        person = Person()
        with self.assertRaises(AttributeError):
            password = person.password

    def test_004_set_password(self):
        person = Person(
            name='Test 001.004'
        )

        person.password = 'simple'

        db.session.add(person)
        db.session.commit()

    def test_005_no_second_factor(self):
        person = Person(
            name='Test 001.005'
        )

        self.assertFalse(person.second_factor)

    def test_006_verify_password(self):
        person = Person(
            name='Test 001.006'
        )

        person.password = 'simple'

        db.session.add(person)
        db.session.commit()

        self.assertFalse(person.verify_password('blabla'))
        db.session.commit()

        self.assertTrue(person.verify_password('simple'))
        db.session.commit()

    def test_007_to_dict(self):
        person = Person(
            name='Test 001.006'
        )

        self.assertIsInstance(person.to_dict(), dict)
