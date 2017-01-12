import datetime
import random
import sys
import time
import unittest

sys.path.insert(0, '.')

from piko.apps.candlepin.db.model import Customer
from piko.apps.candlepin.db.model import Entitlement
from piko.apps.candlepin.db.model import Product
from piko.apps.candlepin.db.model import Subscription
from piko.apps.candlepin.db.model import System

from piko.db import db

class TestCandlepin(unittest.TestCase):
    def test_000_customers(self):
        ke14 = db.session.query(Product).filter_by(key = 'kolab-14').first()
        ke14ea = db.session.query(Product).filter_by(key = 'kolab-14-extras-audit').first()

        for x in range(0,random.randint(20,100)):
            # Randomize the start dates for the customers between now and
            # 10 years ago.
            fake_start_delta = random.randint(
                    0,
                    # 10 years
                    60 * 60 * 24 * 7 * 52 * 10
                )

            customer = Customer(
                    name = "Customer #%06d" % (x),
                    created = datetime.datetime.fromtimestamp(
                            (int)(time.time()) - fake_start_delta
                        )
                )

            db.session.add(customer)

            # Commit only after the entire transaction is complete
            #db.session.commit()

            end_date = None

            if random.randint(1,100) < 60:
                end_date = datetime.datetime.fromtimestamp(
                        (int)(time.time()) - fake_start_delta
                    ) + datetime.timedelta(days=60)

            entitlement = Entitlement(
                    customer_id = customer.id,
                    product_id = ke14.id,
                    quantity = random.randint(1,75),
                    start_date = datetime.datetime.fromtimestamp(
                            (int)(time.time()) - fake_start_delta
                        ),
                    end_date = end_date
                )

            db.session.add(entitlement)

            if random.randint(1,100) < 10:
                entitlement = Entitlement(
                        customer_id = customer.id,
                        product_id = ke14ea.id,
                        quantity = random.randint(1,75),
                        start_date = datetime.datetime.fromtimestamp(
                                (int)(time.time()) - fake_start_delta
                            ),
                        end_date = end_date
                    )

                db.session.add(entitlement)

            # Commit only after the entire transaction is complete
            #db.session.commit()

            for x in range(0,random.randint(2,150)):
                system = System(customer = customer)
                db.session.add(system)

                # Commit only after the entire transaction is complete
                #db.session.commit()

                subscription = Subscription(
                        entitlement_id = entitlement.id,
                        system_id = system.id
                    )

                db.session.add(subscription)
                # Commit only after the entire transaction is complete
                #db.session.commit()

            db.session.commit()

    def test_000_system(self):
        for i in range(0,100):
            system = System()
            db.session.add(system)

        db.session.commit()

if __name__ == "__main__":
    unittest.main()
