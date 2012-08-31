# vim: et:sta:bs=2:sw=4:
from django import forms
import kn.leden.entities as Es
import datetime

class EntityChoiceField(forms.ChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs['choices'] = [(e._id, unicode(e.humanName))
                    for e in  kwargs['choices']]
        if kwargs.get('sort_choices', False):
            kwargs['choices'].sort(cmp=lambda x,y: cmp(x[1],y[1]))
            del kwargs['sort_choices']
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
            choices=Es.institutes(), sort_choices=True)
    study = EntityChoiceField(label="Studie",
            choices=Es.studies(), sort_choices=True)
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
            choices=filter(lambda x: not x.is_virtual, Es.groups()),
            sort_choices=True,
            initial=lambda: str(Es.by_name('secretariaat')._id))

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
