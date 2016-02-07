import datetime
import json

from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms.widgets import flatatt
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django import forms

import kn.leden.entities as Es

class EntityChoiceFieldWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        if '_type' in kwargs:
            self.type = kwargs['_type']
            del kwargs['_type']
        else:
            self.type = None
        super(EntityChoiceFieldWidget, self).__init__(*args, **kwargs)
    def render(self, name, value=None, attrs=None):
        final_attrs = self.build_attrs(attrs, name=name)
        code_set_value = ''
        if value:
            code_set_value = (
                '''entityChoiceField_set(%(id)s, %(value)s);'''
                %{'id': json.dumps(final_attrs['id']),
                  'value': json.dumps(str(value))})
        return mark_safe(
            u'''<input type='hidden' id=%(id)s name=%(name)s />
                <script type='text/javascript'>//<!--
                $(function(){
                    create_entityChoiceField(%(id)s, %(params)s);
                    %(code_set_value)s
                });//--></script>'''
                %{'name': json.dumps(name),
                  'id': json.dumps(final_attrs['id']),
                  'params': json.dumps({'type': self.type}),
                  'code_set_value': code_set_value})


class EntityChoiceField(forms.CharField):
    def __init__(self, *args, **kwargs):
        if '_type' in kwargs:
            _type = kwargs['_type']
            del kwargs['_type']
        else:
            _type = None
        kwargs['widget'] = EntityChoiceFieldWidget(_type=_type)
        super(EntityChoiceField, self).__init__(*args, **kwargs)

def validate_username(username):
    if username in Es.names():
        raise ValidationError('Gebruikersnaam is al in gebruik')

class AddUserForm(forms.Form):
    last_name = forms.CharField(label="Achternaam",
                    widget=forms.TextInput(attrs={
                        'placeholder': 'bijv.: Vaart, van der',
                        'oninput': 'update_username()'}))
    first_name = forms.CharField(label="Voornaam",
                    widget=forms.TextInput(attrs={
                        'oninput': 'update_username()'}))
    username = forms.CharField(label="Gebruikersnaam",
                    validators=[validate_username])
    gender = forms.ChoiceField(label="Geslacht", choices=(('m', 'Man'),
                               ('v', 'Vrouw')))
    email = forms.EmailField(label="E-Mail adres")
    dateOfBirth = forms.DateField(label="Geboortedatum")
    addr_street = forms.CharField(label="Straatnaam")
    addr_number = forms.CharField(label="Huisnummer")
    addr_zip = forms.CharField(label="Postcode")
    addr_city = forms.CharField(label="Woonplaats")
    telephone = forms.CharField(label="Telefoonnummer",
                    widget=forms.TextInput(attrs={
                        'placeholder': 'bijv.: +31612345678'}))
    study_number = forms.CharField(label="Studentnummer")
    study_inst = EntityChoiceField(label="Onderwijs instelling",
            _type='institute')
    study = EntityChoiceField(label="Studie",
            _type='study')
    dateJoined = forms.DateField(label="Datum van inschrijving",
            initial=datetime.date.today)
    incasso = forms.BooleanField(label='Incasso', required=False)
    addToList = forms.MultipleChoiceField(label="Voeg toe aan groepen",
            choices=[('eerstejaars', 'Eerstejaars'), ('aan', "Aan"),
                     ('uit', "Uit"), ('zooi', 'Zooi')],
            initial=['leden', 'eerstejaars', 'aan'],
            widget=forms.CheckboxSelectMultiple())

class AddGroupForm(forms.Form):
    name = forms.RegexField(label="Naam", regex=r'^[a-z0-9-]{2,64}$')
    humanName = forms.CharField(label="Naam voor mensen")
    genitive_prefix = forms.CharField(label="Genitivus", initial="van de")
    description = forms.CharField(label="Korte beschrijving")
    parent = EntityChoiceField(label="Parent",
            _type='group',
            initial=Es.by_name('secretariaat')._id)
    true_group = forms.BooleanField(label="Volwaardige groep",
            initial=True)

class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput())
    new_password = forms.CharField(widget=forms.PasswordInput())
    new_password_again = forms.CharField(widget=forms.PasswordInput())

    def clean(self):
        errors = []
        cleaned_data = self.cleaned_data

        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        new_password_again = cleaned_data.get("new_password_again")

        # todo: add proper and not hardcoded localization

        if not old_password:
            errors.append("geen oud wachtwoord opgegeven")
        if not new_password:
            errors.append("geen nieuw wachtwoord opgegeven")
        if new_password != new_password_again:
            errors.append("niet hetzelfde nieuwe wachtwoord "
                    "opnieuw gegeven")
        if len(errors)>0:
            raise forms.ValidationError(errors)

        return cleaned_data

# vim: et:sta:bs=2:sw=4:
