# vim: et:sta:bs=2:sw=4:
from django import forms
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from django.forms.widgets import flatatt
import kn.leden.entities as Es
import datetime
import json

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
        if value:
            final_attrs['value'] = escape(value)
        if not final_attrs.has_key('id'):
            final_attrs['id'] = 'id_%s' % name
        del final_attrs['name']
        return mark_safe(
            u'''<input type='text' %(attrs)s />
                <input type='hidden' id=%(id2)s name=%(name)s />
                <script type='text/javascript'>//<!--
                $(%(hid)s).autocomplete({
                    source: function(request, response) {
                        $.post(%(api_url)s, {
                            csrfmiddlewaretoken: csrf_token,
                            data: JSON.stringify({
                                action: "entities_by_keyword",
                                keyword: request.term,
                                type: %(type)s
                            })
                        }, function(data) {
                            response($.map(data, function(item) {
                                return {label: item[1], value: item[0]};
                            }));
                        }, "json");
                    }, select: function(event, ui) {
                        $(%(hid)s).val(ui.item.label);
                        $(%(hid2)s).val(ui.item.value);
                        return false;
                    }, minLength: 0}).focus(function() {
                        $(this).trigger('keydown.autocomplete');
                    });
                //--></script>''' % {
                                 'attrs': flatatt(final_attrs),
                                 'name': json.dumps(name),
                                 'id2': json.dumps(final_attrs['id']+'2'),
                                 'hid': json.dumps('#'+final_attrs['id']),
                                 'hid2': json.dumps('#'+final_attrs['id']+'2'),
                                 'type': json.dumps(self.type),
                                 'api_url': json.dumps(reverse('leden-api'))})


class EntityChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        if '_type' in kwargs:
            _type = kwargs['_type']
            del kwargs['_type']
        else:
            _type = None
        kwargs['widget'] = EntityChoiceFieldWidget(_type=_type)
        super(EntityChoiceField, self).__init__(*args, **kwargs)

class AddUserForm(forms.Form):
    last_name = forms.CharField(label="Achternaam")
    first_name = forms.CharField(label="Voornaam")
    sex = forms.ChoiceField(label="Geslacht", choices=(('m', 'Man'),
                               ('v', 'Vrouw')))
    email = forms.EmailField(label="E-Mail adres")
    dateOfBirth = forms.DateField(label="Geboortedatum")
    addr_street = forms.CharField(label="Straatnaam")
    addr_number = forms.CharField(label="Huisnummer")
    addr_zip = forms.CharField(label="Postcode")
    addr_city = forms.CharField(label="Woonplaats")
    telephone = forms.CharField(label="Telefoonnummer")
    study_number = forms.CharField(label="Studentnummer")
    study_inst = EntityChoiceField(label="Onderwijs instelling",
            _type='institute')
    study = EntityChoiceField(label="Studie",
            _type='study')
    dateJoined = forms.DateField(label="Datum van inschrijving",
            initial=datetime.date.today)
    addToList = forms.MultipleChoiceField(label="Voeg toe aan maillijsten",
            choices=[('aan', "aan"), ('uit', "uit")], initial=['aan'],
            widget=forms.CheckboxSelectMultiple())

class AddGroupForm(forms.Form):
    name = forms.RegexField(label="Naam", regex=r'^[a-z0-9-]{2,64}$')
    humanName = forms.CharField(label="Naam voor mensen")
    genitive_prefix = forms.CharField(label="Genitivus", initial="van de")
    description = forms.CharField(label="Korte beschrijving")
    parent = EntityChoiceField(label="Parent",
            _type='group',
            initial=lambda x: str(Es.by_name('secretariaat')._id))

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
