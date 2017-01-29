import datetime
import json

import reserved

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

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
                % {'id': json.dumps(final_attrs['id']),
                   'value': json.dumps(str(value))})
        return mark_safe(
            u'''<input type='hidden' id=%(id)s name=%(name)s />
                <script type='text/javascript'>//<!--
                $(function(){
                    create_entityChoiceField(%(id)s, %(params)s);
                    %(code_set_value)s
                });//--></script>'''
            % {'name': json.dumps(name),
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
        raise forms.ValidationError(_('Gebruikersnaam is al in gebruik'))
    if any(map(lambda c: c not in settings.USERNAME_CHARS, username)):
        raise forms.ValidationError(
            _('Gebruikersnaam bevat een niet-toegestane letter'))
    if not reserved.allowed(username):
        raise forms.ValidationError(_('Gebruikersnaam is niet toegestaan'))


class AddUserForm(forms.Form):
    first_name = forms.CharField(label=_("Voornaam"))
    last_name = forms.CharField(
        label=_("Achternaam"),
        widget=forms.TextInput(
            attrs={
                'placeholder': _('bijv.: Vaart, van der')}))
    username = forms.CharField(label=_("Gebruikersnaam"),
                               validators=[validate_username])
    email = forms.EmailField(label=_("E-Mail adres"))
    dateOfBirth = forms.DateField(label=_("Geboortedatum"))
    addr_street = forms.CharField(label=_("Straatnaam"))
    addr_number = forms.CharField(label=_("Huisnummer"))
    addr_zip = forms.CharField(label=_("Postcode"))
    addr_city = forms.CharField(label=_("Woonplaats"))
    telephone = forms.CharField(label=_("Telefoonnummer"),
                                widget=forms.TextInput(attrs={
                                    'placeholder': _('bijv.: +31612345678')}))
    study_number = forms.CharField(label=_("Studentnummer"), required=False)
    study_inst = EntityChoiceField(label=_("Onderwijs instelling"),
                                   _type='institute')
    study = EntityChoiceField(label=_("Studie"),
                              _type='study')
    dateJoined = forms.DateField(label=_("Datum van inschrijving"),
                                 initial=datetime.date.today)
    incasso = forms.BooleanField(label=_('Incasso'), required=False)
    addToList = forms.MultipleChoiceField(
        label=_("Voeg toe aan groepen"),
        choices=[('eerstejaars', _('Eerstejaars')), ('aan', _("Aan")),
                 ('uit', _("Uit")), ('zooi', _('Zooi'))],
        initial=['leden', 'eerstejaars', 'aan'],
        required=False,
        widget=forms.CheckboxSelectMultiple()
    )


class AddGroupForm(forms.Form):
    name = forms.RegexField(label=_("Naam"), regex=r'^[a-z0-9-]{2,64}$')
    humanName = forms.CharField(label=_("Naam voor mensen"))
    genitive_prefix = forms.CharField(label=_("Genitivus"), initial="van de")
    description = forms.CharField(label=_("Korte beschrijving"))
    parent = EntityChoiceField(label=_("Oudergroep"),
                               _type='group',
                               initial=Es.by_name('groepen')._id)
    true_group = forms.BooleanField(label=_("Volwaardige groep"),
                                    initial=True)


class AddStudyForm(forms.Form):
    study = EntityChoiceField(label=_('Studie'), _type='study')
    study_inst = EntityChoiceField(label=_('Onderwijs instelling'),
                                   _type='institute')
    study_number = forms.CharField(label=_('Studentnummer'), required=False)
    study_from = forms.DateField(label=_('Start op'),
                                 initial=datetime.date.today)


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

        if not old_password:
            errors.append(_("Geen oud wachtwoord opgegeven"))
        if not new_password:
            errors.append(_("Geen nieuw wachtwoord opgegeven"))
        if new_password != new_password_again:
            errors.append(_("Niet hetzelfde nieuwe wachtwoord "
                            "opnieuw gegeven"))
        if len(errors) > 0:
            raise forms.ValidationError(errors)

        return cleaned_data

# vim: et:sta:bs=2:sw=4:
