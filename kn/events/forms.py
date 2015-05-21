from django import forms

from kn.leden.forms import EntityChoiceField
from kn.leden.forms import EntityChoiceFieldWidget
import kn.leden.entities as Es

def get_add_event_form(user, superuser=False):
    class AddEventForm(forms.Form):
        name = forms.RegexField(
                label='Korte naam',
                regex=r'^[a-z0-9-]+$',
                widget=forms.TextInput(attrs={
                    'class': 'mediumfield'})
        )
        humanName = forms.CharField(
                label='Naam',
                widget=forms.TextInput(attrs={
                    'class': 'hugefield'})
        )
        description = forms.CharField(
                label='Beschrijving',
                widget=forms.Textarea(attrs={
                    'rows': '5'})
        )
        msg_subscribed = forms.CharField(
                label='E-Mail wanneer aangemeld',
                widget=forms.Textarea,
                initial="Hallo %(firstName)s,\n\n"+
                    "Je hebt je aangemeld voor %(eventName)s.\n"+
                    "\n"+
                    "Je opmerkingen waren:\n"+
                    "%(notes)s\n"+
                    "\n"+
                    "Met een vriendelijke groet,\n\n"+
                    "%(owner)s")
        msg_subscribedBy = forms.CharField(
                label='E-Mail wanneer aangemeld door een ander',
                widget=forms.Textarea,
                initial="Hallo %(firstName)s,\n\n"+
                    "Je bent door %(by_firstName)s aangemeld "+
                        "voor %(eventName)s.\n"+
                    "\n"+
                    "%(by_firstName)s opmerkingen waren:\n"+
                    "%(by_notes)s\n"+
                    "\n"+
                    "Om deze aanmelding te bevestigen, bezoek:\n"
                    "  %(confirmationLink)s\n"+
                    "\n"+
                    "Met een vriendelijke groet,\n\n"+
                    "%(owner)s")
        msg_confirmed = forms.CharField(
                label='E-Mail wanneer aanmelding is bevestigd',
                widget=forms.Textarea,
                initial="Hallo %(firstName)s,\n\n"+
                    "Je hebt je aanmelding voor %(eventName)s bevestigd.\n\n"+
                    "Met een vriendelijke groet,\n\n"+
                    "%(owner)s")
        cost = forms.DecimalField(
                label='Kosten',
                widget=forms.TextInput(attrs={
                    'class': 'smallfield'
                })
        )
        when = forms.DateField(
                label='Datum'
        )
        owner = EntityChoiceField(
                label='Eigenaar',
                widget=EntityChoiceFieldWidget(attrs={
                    'class': 'mediumfield'})
        )
        has_public_subscriptions = forms.BooleanField(
                required=False,
                label='Inschrijvingen openbaar'
        )
        owner_can_subscribe_others = forms.BooleanField(
                required=False,
                label='Eigenaar kan iedereen inschrijven'
        )
        anyone_can_subscribe_others = forms.BooleanField(
                required=False,
                label='Iedereen kan iedereen inschrijven'
        )
    return AddEventForm

# vim: et:sta:bs=2:sw=4:
