from django import forms

from kn.leden.forms import EntityChoiceField
import kn.leden.entities as Es

import textwrap

def get_add_event_form(user, superuser=False):
    class AddEventForm(forms.Form):
        name = forms.RegexField(label='Korte naam', regex=r'^[a-z0-9-]+$')
        humanName = forms.CharField(label='Naam')
        description = forms.CharField(label='Beschrijving',
                widget=forms.Textarea)
        cost = forms.DecimalField(label='Kosten')
        date = forms.DateField(label='Datum')
        max_subscriptions = forms.IntegerField(required=False,
                label='Maximum aantal deelnemers (optioneel)')
        owner = EntityChoiceField(label="Eigenaar")
        has_public_subscriptions = forms.BooleanField(required=False,
                label='Inschrijvingen openbaar')
        may_unsubscribe = forms.BooleanField(required=False, initial=True,
                label='Leden mogen zichzelf afmelden')
    return AddEventForm

# vim: et:sta:bs=2:sw=4:
