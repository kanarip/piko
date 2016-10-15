from flask.ext.wtf import Form

from wtforms import BooleanField
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import validators

class SignupEmailForm(Form):
    email_address = TextField('Email Address', validators=[validators.Required(), validators.Email()])
    password = PasswordField('Password', validators=[validators.Required()])
    password_again = PasswordField('Password again',
                                   validators=[validators.Required(), validators.EqualTo('password')])
    submit = SubmitField('Register')
