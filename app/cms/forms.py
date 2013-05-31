from yweb.forms import Form
from wtforms import BooleanField, TextField, \
    validators, DateTimeField, TextAreaField, IntegerField, \
    PasswordField, FileField, HiddenField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError


class CategoryForm(Form):

    parent = SelectField( _('Parent Category') )

    name = TextField( _('Name'), [
            validators.Length(min=2, max=64) ] )

    summary = TextAreaField( _('Summary'), [
            validators.Length(max=256) ] )

    description = TextAreaField( _('Description'), [
            validators.Length(max=10240) ] )


class ArticleForm(Form):

    category = SelectField( _('Category') )

    name = TextField( _('Name'), [
            validators.Length(min=2, max=256) ] )

    summary = TextAreaField( _('Summary'), [
            validators.Length(max=1024) ] )

    body = TextAreaField( _('Body'), [
            validators.Length(max=10240) ] )
