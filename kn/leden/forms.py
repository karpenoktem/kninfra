from django import forms

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

