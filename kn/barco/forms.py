import datetime

from django import forms

class FormMeta(forms.Form):
    formname = forms.RegexField(label="Formuliernaam", regex=r'\d{3}')
    jsondata = forms.CharField(widget=forms.HiddenInput())


class BarformMeta(FormMeta):
    pricebase = forms.ChoiceField(label="Prijsbasis", choices=
                    [('v9a', 'v9a'), ('v8a', 'v8a')])
    date = forms.DateField(label="Datum", initial=datetime.date.today())
    tapper = forms.CharField(label="Tapper")
    dienst = forms.CharField(label="Dienst")
    beginkas = forms.DecimalField(label="Beginkas")
    eindkas = forms.DecimalField(label="Eindkas")
    comments = forms.CharField(label="Opmerkingen",
                    widget=forms.widgets.Textarea(), required=False)


class InvCountMeta(FormMeta):
    date = forms.DateField(label="Datum", initial=datetime.date.today())
    tellers = forms.CharField(label="Tellers")
    comments = forms.CharField(label="Opmerkingen",
                    widget=forms.widgets.Textarea(), required=False)
