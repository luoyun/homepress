from yweb.forms import Form
from wtforms import BooleanField, TextField, \
    validators, DateTimeField, TextAreaField, IntegerField, \
    PasswordField, FileField, HiddenField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError


from .models import CRMCustomer
class CRMCustomerForm(Form):

    name = TextField( _('Name'), [
            validators.Length(min=2, max=64) ] )

    description = TextAreaField( _('Description'), [
            validators.Length(max=1024*10) ] )


class CRMCustomerAddForm(CRMCustomerForm):

    def validate_name(form, field):
        old = form._handler.db.query(CRMCustomer).filter_by(
            name = field.data).first()
        if old:
            raise ValidationError( _('This customer was exist.') )


from .models import CRMContact
class CRMContactForm(Form):

    name = TextField( _('Name'), [
            validators.Length(min=2, max=64) ] )

    nickname = TextField( _('Nickname'), [
            validators.Length(max=64) ] )

    description = TextAreaField( _('Description'), [
            validators.Length(max=1024*10) ] )


class CRMContactAddForm(CRMContactForm):

    pass


class CRMContactDetailAddForm(Form):

    type = SelectField( _('Type') )

    data = TextField( _('Value'), [
            validators.Length(min=2, max=64) ] )

    desc = TextField( _('Desc'), [
            validators.Length(max=128) ] )



class CRMContactInteractionForm(Form):

    type = SelectField( _('Type') )

    summary = TextField( _('Summary'), [
            validators.Length(min=2, max=512) ] )

    description = TextAreaField( _('Description'), [
            validators.Length(max=1024*10) ] )

    started = DateTimeField( _('Started Date') )
    ended = DateTimeField( _('Ended Date') )
