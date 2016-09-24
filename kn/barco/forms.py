import datetime

from django import forms
from django.utils.translation import ugettext as _

class FormMeta(forms.Form):
    formname = forms.RegexField(label=_("Formuliernaam"), regex=r'\d{3}')
    jsondata = forms.CharField(widget=forms.HiddenInput())


class BarformMeta(FormMeta):
    pricebase = forms.ChoiceField(label=_("Prijsbasis"), choices=
                    [('v9a', 'v9a'), ('v8a', 'v8a')])
    date = forms.DateField(label=_("Datum"), initial=datetime.date.today())
    tapper = forms.CharField(label=_("Tapper"))
    dienst = forms.CharField(label=_("Dienst"))
    beginkas = forms.DecimalField(label=_("Beginkas"))
    eindkas = forms.DecimalField(label=_("Eindkas"))
    comments = forms.CharField(label=_("Opmerkingen"),
                    widget=forms.widgets.Textarea(), required=False)


class InvCountMeta(FormMeta):
    date = forms.DateField(label=_("Datum"), initial=datetime.date.today())
    tellers = forms.CharField(label=_("Tellers"))
    comments = forms.CharField(label=_("Opmerkingen"),
                    widget=forms.widgets.Textarea(), required=False)
