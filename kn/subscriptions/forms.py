from django import forms

from kn.leden.forms import EntityChoiceField
from kn.leden.mongo import _id
import kn.leden.entities as Es
import kn.subscriptions.entities as subscr_Es

import textwrap

def get_allowed_owners(user):
    '''
    Get the entities (often groups) that this owner is allowed to use.
    Does not check for superuser capabilities (which may select any entity).
    '''

    entities = [user] + [g for g in user.cached_groups
                           if subscr_Es.may_set_owner(user, g)]
    return entities

def validate_event_name(name):
    if subscr_Es.event_by_name(name):
        raise forms.ValidationError('Naam voor computers bestaat al')


def get_add_event_form(user, superuser=False, editing=False):
    class AddEventForm(forms.Form):
        humanName = forms.CharField(label='Naam',
                widget=forms.TextInput(attrs={'required': ''}))
        if not editing:
            name = forms.RegexField(label='Naam voor computers',
                    regex=r'^[a-z0-9-]+$',
                    widget=forms.TextInput(attrs={
                        'required': '',
                        'pattern':  '[a-z0-9-]+'}),
                    validators=[validate_event_name])
        description = forms.CharField(label='Beschrijving',
                widget=forms.Textarea(attrs={'required': ''}))
        cost = forms.DecimalField(label='Kosten',
                initial='0',
                widget=forms.NumberInput(attrs={
                    'required': '',
                    'min':      '0'}))
        date = forms.DateField(label='Datum',
                widget=forms.DateInput(attrs={
                    'required':    '',
                    'placeholder': 'jjjj-mm-dd'}))
        max_subscriptions = forms.IntegerField(required=False,
                label='Maximum aantal deelnemers (optioneel)',
                widget=forms.NumberInput(attrs={'placeholder': 'geen maximum'}))
        if superuser:
            owner = EntityChoiceField(label="Eigenaar")
        else:
            owner = forms.ChoiceField(label='Eigenaar',
                                      choices=[(_id(e), unicode(e.humanName))
                                               for e in get_allowed_owners(user)])
        has_public_subscriptions = forms.BooleanField(required=False,
                label='Inschrijvingen openbaar')
        may_unsubscribe = forms.BooleanField(required=False, initial=False,
                label='Leden mogen zichzelf afmelden')
    return AddEventForm

# vim: et:sta:bs=2:sw=4:
