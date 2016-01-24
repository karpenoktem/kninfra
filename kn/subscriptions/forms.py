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
        subscribedMailBody = forms.CharField(label='E-Mail wanneer aangemeld',
            widget=forms.Textarea,
            initial="Hallo %(firstName)s,\n\n"+
                "Je hebt je aangemeld voor %(eventName)s.\n"+
                "\n"+
                "Je opmerkingen waren:\n"+
                "%(notes)s\n"+
                "\n"+
                "Met een vriendelijke groet,\n\n"+
                "%(owner)s")
        invitedMailBody = forms.CharField(
            label='E-Mail wanneer uitgenodigd',
            widget=forms.Textarea,
            initial=textwrap.dedent("""
                Hallo %(firstName)s,

                Je bent door %(by_firstName)s uitgenodigd voor %(eventName)s.

                %(by_firstName)s opmerkingen waren:

                  %(by_notes)s

                Om je aanmelding te bevestigen, ga naar de volgende pagina
                en druk op `aanmelden'.

                  %(confirmationLink)s

                %(owner)s
                """).strip())
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
    return AddEventForm

# vim: et:sta:bs=2:sw=4:
