from ..forms import Form
from wtforms import StringField, validators, SelectField, SelectMultipleField, IntegerField


class SearchForm(Form):

    search = StringField('Indicator', [validators.DataRequired()])

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

    def validate(self):
        return super(SearchForm, self).validate()

    def populate_obj(self, obj):
        super(SearchForm, self).populate_obj(obj)

