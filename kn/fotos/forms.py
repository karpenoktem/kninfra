import os
from glob import glob
from datetime import date
from collections import namedtuple

from django import forms

from kn.settings import PHOTOS_DIR, USER_DIRS, WOLK_PATH

import kn.fotos.entities as fEs

foto_root = namedtuple('foto_root', ('root', 'between'))
foto_dirs = {'home': foto_root(USER_DIRS, 'fotos'),
             'wolk': foto_root(os.path.join(WOLK_PATH, 'data'), 'files/Photos')}

def move_fotos_scan_userdirs():
    for source, (root, between) in foto_dirs.items():
        for user in os.listdir(root):
            if user[0] == '.':
                continue
            fd = os.path.join(root, user, between)
            if not os.path.isdir(fd):
                continue
            for dir in os.listdir(fd):
                if fd[0] == '.' or not os.path.isdir(os.path.join(fd, dir)):
                    continue
                n = user+'/'+dir
                yield (source+'/'+n, n)

def list_events():
    events = []
    for album in fEs.by_path('').list_all():
        events.append(album.name)
    events.sort(reverse=True)
    return events

def move_fotos_list_events():
    return map(lambda x: (x, x), list_events())

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
