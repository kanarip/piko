"""
    piko.forms.LoginEmailForm
    =========================

    Provides a CSRF-protected login form for use with an email address and
    password.
"""

# pylint: disable=no-name-in-module
# pylint: disable=import-error
from flask.ext.wtf import Form

from wtforms import HiddenField
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import validators


# pylint: disable=too-few-public-methods
class LoginEmailForm(Form):
    """
        A :py:class:`Form` definition.
    """
    uuid = HiddenField('UUID')

    email_address = TextField(
        'Email Address',
        validators=[
            validators.Required(),
            validators.Email()
        ]
    )

    password = PasswordField('Password', validators=[validators.Required()])

    submit = SubmitField('Login')
