import os
from glob import glob
from datetime import date

from django import forms

from kn.settings import PHOTOS_DIR, USER_DIRS

def move_fotos_scan_userdirs():
    # XXX os.path.join?
    for user in os.listdir(USER_DIRS):
        if user[0] == '.':
            continue
        fd = '%s%s/fotos/' % (USER_DIRS, user)
        if not os.path.isdir(fd):
            continue
        for dir in os.listdir(fd):
            if fd[0] == '.' or not os.path.isdir(fd + dir):
                continue
            n = '%s/%s' % (user, dir)
            yield (n,n)

def move_fotos_list_events():
    events = list(map(os.path.basename, glob('%s/20*' % PHOTOS_DIR)))
    events.sort(reverse=True)
    return map(lambda x: (x, x), events)

class CreateEventForm(forms.Form):
    humanName = forms.CharField(label='Naam voor mensen')
    date = forms.DateField(label='Datum', initial=date.today)
    name = forms.RegexField(label='Naam voor computers',
            regex=r'^[a-z0-9-]{3,64}$')
    fullHumanName = forms.CharField(label='Volledige naam voor mensen')

    date.widget.attrs['onblur'] = 'createFullHumanname();'
    humanName.widget.attrs['onblur'] = ('createTechName(); '+
                        'createFullHumanname();')

def getMoveFotosForm():
    class MoveFotosForm(forms.Form):
        move_src = forms.ChoiceField(label='Verplaats',
                choices=move_fotos_scan_userdirs())
        move_dst = forms.ChoiceField(label='naar',
                choices=move_fotos_list_events())
    return MoveFotosForm

# vim: et:sta:bs=2:sw=4:
