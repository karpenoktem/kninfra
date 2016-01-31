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
        unsubscribedMailBody = forms.CharField(label='E-Mail wanneer afgemeld',
            widget=forms.Textarea,
            initial="Hallo %(firstName)s,\n\n"+
                "Je hebt je afgemeld voor %(eventName)s.\n"+
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
        owner = EntityChoiceField(label="Eigenaar")
        has_public_subscriptions = forms.BooleanField(required=False,
                label='Inschrijvingen openbaar')
        may_unsubscribe = forms.BooleanField(required=False, initial=True,
                label='Leden mogen zichzelf afmelden')
    return AddEventForm

# vim: et:sta:bs=2:sw=4:
