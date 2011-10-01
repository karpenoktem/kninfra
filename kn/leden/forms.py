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
                        initial=datetime.date.today())

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

