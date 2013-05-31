from yweb.forms import Form
from wtforms import BooleanField, TextField, \
    validators, DateTimeField, TextAreaField, IntegerField, \
    PasswordField, FileField

from wtforms.validators import ValidationError


def password_confirm(form, field):
    if field.data != form.password_confirm.data:
        raise ValidationError( _('password confirm failed') )


class LoginForm(Form):
    username = TextField( _('Username') )
    password = PasswordField( _('Password') )

