from datetime import date

from django import forms
from django.utils.translation import ugettext as _

import kn.fotos.entities as fEs
from kn.leden import giedo


def list_events():
    events = []
    for album in fEs.by_path('').list_all():
        events.append(album.name)
    events.sort(reverse=True)
    return events


class CreateEventForm(forms.Form):
    humanName = forms.CharField(label=_('Naam voor mensen'))
    date = forms.DateField(label=_('Datum'), initial=date.today)
    name = forms.RegexField(label=_('Naam voor computers'),
                            regex=r'^[a-z0-9-]{3,64}$')
    fullHumanName = forms.CharField(label=_('Volledige naam voor mensen'))

    date.widget.attrs['onblur'] = 'createFullHumanname();'
    humanName.widget.attrs['onblur'] = ('createTechName(); ' +
                                        'createFullHumanname();')


# vim: et:sta:bs=2:sw=4:
