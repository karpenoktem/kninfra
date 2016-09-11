from datetime import date

from django.utils.translation import ugettext as _
from django import forms

from kn.leden import giedo

import kn.fotos.entities as fEs


def list_events():
    events = []
    for album in fEs.by_path('').list_all():
        events.append(album.name)
    events.sort(reverse=True)
    return events

def move_fotos_list_events():
    return map(lambda x: (x, x), list_events())

class CreateEventForm(forms.Form):
    humanName = forms.CharField(label=_('Naam voor mensen'))
    date = forms.DateField(label=_('Datum'), initial=date.today)
    name = forms.RegexField(label=_('Naam voor computers'),
            regex=r'^[a-z0-9-]{3,64}$')
    fullHumanName = forms.CharField(label=_('Volledige naam voor mensen'))

    date.widget.attrs['onblur'] = 'createFullHumanname();'
    humanName.widget.attrs['onblur'] = ('createTechName(); '+
                        'createFullHumanname();')

def getMoveFotosForm():
    class MoveFotosForm(forms.Form):
        move_src = forms.ChoiceField(label=_('Verplaats'),
                choices=giedo.fotoadmin_scan_userdirs())
        move_dst = forms.ChoiceField(label=_('naar'),
                choices=move_fotos_list_events())
    return MoveFotosForm

# vim: et:sta:bs=2:sw=4:
