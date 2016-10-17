import sys
import unittest

sys.path.insert(0, '.')

from piko.apps.candlepin.db.model import System

from piko.db import db

class TestCandlepin(unittest.TestCase):
    def test_000_systems(self):
        system = System()
        db.session.add(system)
        db.session.commit()

if __name__ == "__main__":
    unittest.main()
