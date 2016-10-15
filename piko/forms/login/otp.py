from flask.ext.wtf import Form

from wtforms import HiddenField
from wtforms import IntegerField
from wtforms import SubmitField
from wtforms import validators

class LoginOTPForm(Form):
    uuid = HiddenField('UUID')
    otp = IntegerField('Token', validators=[validators.Required(), validators.NumberRange(min=0, max=999999)])
    submit = SubmitField('Submit')
