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
                name = forms.CharField(label='Korte naam')
                humanName = forms.CharField(label='Naam')
                description = forms.CharField(label='Beschrijving',
                                widget=forms.Textarea)
                mailBody = forms.CharField(label='E-Mail',
                        widget=forms.Textarea,
                        initial="Hallo %(firstName)s,\n\n"+
                                "Je hebt je aangemeld voor %(eventName)s.\n"+
                                "\n"+
                                "Je opmerkingen waren:\n"+
                                "%(notes)s\n"+
                                "\n"+
                                "Met een vriendelijke groet,\n\n"+
                                "%(owner)s")
                cost = forms.DecimalField(label='Kosten')
                date = forms.DateField(label='Datum')
                owner = EntityChoiceField(label="Eigenaar", choices=choices)
        return AddEventForm
