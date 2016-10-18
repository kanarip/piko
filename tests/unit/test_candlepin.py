import sys
import unittest

sys.path.insert(0, '.')

from piko.apps.candlepin.db.model import Customer
from piko.apps.candlepin.db.model import Entitlement
from piko.apps.candlepin.db.model import Subscription
from piko.apps.candlepin.db.model import System

from piko.db import db

class TestCandlepin(unittest.TestCase):
    def test_000_customers(self):
        for x in range(0,10):
            customer = Customer(name="Customer #%06d" % (x))
            db.session.add(customer)
            #db.session.commit()

            entitlement = Entitlement(customer_id=customer.id, product_id=1, quantity=10)
            db.session.add(entitlement)
            #db.session.commit()

            for x in range(0,9):
                system = System(customer=customer)
                db.session.add(system)
                #db.session.commit()

                subscription = Subscription(
                        entitlement_id=entitlement.id,
                        system_id=system.id
                    )

                db.session.add(subscription)
                db.session.commit()

    def test_000_system(self):
        for i in range(0,100):
            system = System()
            db.session.add(system)

        db.session.commit()

if __name__ == "__main__":
    unittest.main()
