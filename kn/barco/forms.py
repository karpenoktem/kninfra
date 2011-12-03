from django import forms
import datetime

class BarFormMeta(forms.Form):
    formname = forms.RegexField(label="Formuliernaam", regex=r'\d{3}')
    pricebase = forms.ChoiceField(label="Prijsbasis", choices=[('v8a', 'v8a')])
    date = forms.DateField(label="Datum", initial=datetime.date.today())
    tapper = forms.CharField(label="Tapper")
    dienst = forms.CharField(label="Dienst")
    beginkas = forms.DecimalField(label="Beginkas")
    eindkas = forms.DecimalField(label="Eindkas")
    jsondata = forms.CharField(widget=forms.HiddenInput())
