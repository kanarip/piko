from flask.ext.wtf import Form

from wtforms import HiddenField
from wtforms import TextField
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms import validators

class LoginEmailForm(Form):
    uuid = HiddenField('UUID')
    email_address = TextField('Email Address', validators=[validators.Required(), validators.Email()])
    password = PasswordField('Password', validators=[validators.Required()])
    submit = SubmitField('Login')
