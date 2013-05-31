from yweb.forms import Form
from wtforms import BooleanField, TextField, \
    validators, DateTimeField, TextAreaField, IntegerField, \
    PasswordField, FileField, HiddenField

from wtforms.validators import ValidationError


def password_confirm(form, field):
    if field.data != form.password_confirm.data:
        raise ValidationError( _('password confirm failed') )


class ResetPasswordApplyForm(Form):
    email = TextField( _('Email Address'), [
            validators.Length(min=6, max=35), validators.Email() ] )


class ResetPasswordForm(Form):
    #key = HiddenField( _('Key') )
    password = PasswordField( _('Password'), [
            password_confirm, validators.Length(min=6, max=120) ] )
    password_confirm = PasswordField( _('Confirm Password') )
