"""
    Test the basic piko Flask application called Home.
"""
import os
import unittest

# pylint: disable=no-name-in-module,import-error
from flask.testing import FlaskClient
from flask.ext.fillin import FormWrapper

from piko import App

# pylint: disable=invalid-name
app = App('piko')

#: Holds registered applications.
# pylint: disable=invalid-name
applications = {}

#: The base path to search for additional applications.
# pylint: disable=invalid-name
base_path = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'piko',
        'apps'
    )
)

for candidate in os.listdir(base_path):
    # Must be a directory.
    if not os.path.isdir(os.path.join(base_path, candidate)):
        continue

    mod_name = 'piko.apps.' + candidate

    try:
        # Obtain the register function...
        application = __import__(
            mod_name,
            fromlist=[
                'register',
                'register_blueprint',
                'register_routes'
            ]
        )

        # ...and execute it.
        application.register_blueprint(app)
    except ImportError, errmsg:
        import traceback
        app.logger.error("ImportError: %r" % (errmsg))
        app.logger.error("%s" % (traceback.format_exc()))
    except AttributeError, errmsg:
        import traceback
        app.logger.error("AttributeError: %r" % (errmsg))
        app.logger.error("%s" % (traceback.format_exc()))

class TestHome(unittest.TestCase):
    """
        Test base Flask application Home.
    """
    def setUp(self):
        app.testing = True
        self.client = FlaskClient(app, response_wrapper=FormWrapper)

    def tearDown(self):
        pass

    def test_000_page_index_get(self):
        """
            200, OK: GET /
        """
        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)

    def test_000_page_index_post(self):
        """
            405, Method not allowed: POST /
        """
        result = self.client.post('/')
        self.assertEqual(result.status_code, 405)

    def test_001_page_login_get(self):
        """
            200, OK: GET /login
        """
        result = self.client.get('/login')
        self.assertEqual(result.status_code, 200)

    def test_001_page_login_post(self):
        """
            405, Method not allowed: POST /login
        """
        result = self.client.post('/login')
        self.assertEqual(result.status_code, 405)

    def test_002_page_login_get(self):
        """
            200, OK: GET /login (with session transaction)
        """
        with self.client.session_transaction():
            result = self.client.get('/login')
            self.assertTrue('Set-Cookie' in result.headers)
            self.assertEqual(result.status_code, 200)

    def test_002_page_login_post(self):
        """
            405, Method not allowed: POST /login (with session transaction)
        """
        with self.client.session_transaction():
            result = self.client.post('/login')
            self.assertEqual(result.status_code, 405)

    def test_003_page_login_email_get(self):
        """
            200, OK: GET /login/email (with session transaction)
        """
        with self.client.session_transaction():
            result = self.client.get('/login/email')
            self.assertTrue('Set-Cookie' in result.headers)
            self.assertEqual(result.status_code, 200)

    def test_004_page_login_otp(self):
        """
            302, Found: GET /login/otp
        """
        result = self.client.get('/login/otp')
        self.assertEqual(result.status_code, 302)

    def test_004_page_login_otp_get(self):
        """
            302, Found: GET /login/otp (with session transaction)
        """
        with self.client.session_transaction():
            result = self.client.get('/login/otp')
            self.assertEqual(result.status_code, 302)

    def test_005_page_login_complete(self):
        """
            403, Access denied: GET /login/complete
        """
        with self.client.session_transaction():
            result = self.client.get('/login/complete')
            self.assertEqual(result.status_code, 403)

    def test_006_page_login_wait(self):
        """
            403, Access denied: GET /login/wait
        """
        with self.client.session_transaction():
            result = self.client.get('/login/wait')
            self.assertEqual(result.status_code, 403)

    def test_007_login_sequence_csrf(self):
        """
            Verify a fixture's login sequence without csrf fails.
        """
        with self.client.session_transaction():
            result = self.client.get('/login')
            self.assertEqual(result.status_code, 200)

            result = self.client.get('/login/email')
            self.assertEqual(result.status_code, 200)

            result.form.fields['email_address'] = 'john@doefamily.org'
            result.form.fields['password'] = 'simple'
            result.form.fields['csrf_token'] = "invalid"

            result = result.form.submit(
                self.client,
                path='/login/email',
                method='POST'
            )

            self.assertEqual(result.status_code, 302)
            self.assertEqual(
                result.headers['Location'],
                "http://localhost/login"
            )

    def test_007_login_sequence_uuid(self):
        """
            Verify a fixture's login sequence with invalid UUID fails.
        """
        with self.client.session_transaction():
            result = self.client.get('/login')
            self.assertEqual(result.status_code, 200)

            result = self.client.get('/login/email')
            self.assertEqual(result.status_code, 200)

            result.form.fields['email_address'] = 'john@doefamily.org'
            result.form.fields['password'] = 'simple'
            result.form.fields['uuid'] = "invalid"

            result = result.form.submit(
                self.client,
                path='/login/email',
                method='POST'
            )

            self.assertEqual(result.status_code, 403)

    def test_007_login_sequence_invalid(self):
        """
            Verify a fixture's login sequence with false password.
        """
        with self.client.session_transaction():
            result = self.client.get('/login')
            self.assertEqual(result.status_code, 200)

            result = self.client.get('/login/email')
            self.assertEqual(result.status_code, 200)

            result.form.fields['email_address'] = 'john@doefamily.org'
            result.form.fields['password'] = 'simple2'

            result = result.form.submit(
                self.client,
                path='/login/email',
                method='POST'
            )

            self.assertEqual(result.status_code, 302)
            self.assertEqual(
                result.headers['Location'],
                "http://localhost/login/wait"
            )

            result = self.client.get('/login/wait')
            self.assertEqual(result.status_code, 200)

    def test_007_login_sequence_valid(self):
        """
            Verify a fixture's login sequence.
        """
        with self.client.session_transaction():
            result = self.client.get('/login')
            self.assertEqual(result.status_code, 200, '/login')

            result = self.client.get('/login/email')
            self.assertEqual(result.status_code, 200, '/login/email')

            result.form.fields['email_address'] = 'john@doefamily.org'
            result.form.fields['password'] = 'simple'

            result = result.form.submit(
                self.client,
                path='/login/email',
                method='POST'
            )

            self.assertEqual(result.status_code, 302)
            self.assertEqual(
                result.headers['Location'],
                "http://localhost/login/wait"
            )

            result = self.client.get('/login/wait')
            self.assertEqual(result.status_code, 200)
