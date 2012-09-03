# vim: et:sta:bs=2:sw=4:
from django import forms
from kn.leden.forms import EntityChoiceField
import kn.leden.entities as Es

def get_add_event_form(user, superuser=False):
    if superuser:
        choices = (sorted(Es.groups(),
                lambda x,y: cmp(unicode(x.humanName),
                    unicode(y.humanName))) +
            sorted(Es.by_name('leden').get_members(),
                lambda x,y: cmp(unicode(x.humanName),
                    unicode(y.humanName))))
    else:
        choices = [user]+sorted(user.cached_groups,
            cmp=lambda x,y: cmp(unicode(x.humanName),
                    unicode(y.humanName)))
    class AddEventForm(forms.Form):
        name = forms.RegexField(label='Korte naam', regex=r'^[a-z0-9-]+$')
        humanName = forms.CharField(label='Naam')
        description = forms.CharField(label='Beschrijving',
                widget=forms.Textarea)
        mailBody = forms.CharField(label='E-Mail wanneer aangemeld',
            widget=forms.Textarea,
            initial="Hallo %(firstName)s,\n\n"+
                "Je hebt je aangemeld voor %(eventName)s.\n"+
                "\n"+
                "Je opmerkingen waren:\n"+
                "%(notes)s\n"+
                "\n"+
                "Met een vriendelijke groet,\n\n"+
                "%(owner)s")
        subscribedByOtherMailBody = forms.CharField(
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
        confirmationMailBody = forms.CharField(
            label='E-Mail wanneer aanmelding is bevestigd',
            widget=forms.Textarea,
            initial="Hallo %(firstName)s,\n\n"+
                "Je hebt je aanmelding voor %(eventName)s bevestigd.\n\n"+
                "Met een vriendelijke groet,\n\n"+
                "%(owner)s")
        cost = forms.DecimalField(label='Kosten')
        date = forms.DateField(label='Datum')
        owner = EntityChoiceField(label="Eigenaar", choices=choices)
        has_public_subscriptions = forms.BooleanField(required=False,
                label='Inschrijvingen openbaar')
        everyone_can_subscribe_others = forms.BooleanField(required=False,
                label='Iedereen kan iedereen inschrijven')
    return AddEventForm
