from flask.ext.bcrypt import Bcrypt

from piko import App
app = App('piko')

bcrypt = Bcrypt(app)

from piko.celery import celery

@celery.task(bind=True)
def generate_password_hash(self, password, rounds=None):
    """
        Generate a password hash using a number of rounds.

        Call **generate_password_hash.delay(``password``, ``rounds``)**
        to submit the job to :py:mod:`celery` workers.
    """
    return bcrypt.generate_password_hash(password, rounds)

@celery.task(bind=True)
def check_password_hash(self, password_hash, password):
    """
        Check a password hash against a password.

        Call **check_password_hash.delay(``password``, ``rounds``)**
        to submit the job to :py:mod:`celery` workers.
    """
    result = bcrypt.check_password_hash(password_hash, password)
    if not result:
        # Do something here.
        return result

    return result
