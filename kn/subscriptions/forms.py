from django import forms

from kn.leden.forms import EntityChoiceField
from kn.leden.mongo import _id
import kn.leden.entities as Es

import textwrap

def get_allowed_owners(user):
    '''
    Get the entities (often groups) that this owner is allowed to use.
    Does not check for superuser capabilities (which may select any entity).
    '''
    # Warning: the actual checking is done in views.event_new_or_edit!
    comms = Es.by_name('comms')
    entities = [user] + \
                [g for g in user.cached_groups if g.has_tag(comms)]
    return entities


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
