from django import forms
from kn.leden.forms import EntityChoiceField
import kn.leden.entities as Es
from datetime import date
import os
from kn.settings import PHOTOS_DIR, USER_DIRS
from glob import glob

def move_fotos_scan_userdirs():
        print "Scanning userdirs for fotos"
        options = list()
        for user in os.listdir(USER_DIRS):
                if user[0] == '.':
                        continue
                fd = '%s%s/fotos/' % (USER_DIRS, user)
                if os.path.isdir(fd):
                        for dir in os.listdir(fd):
                                if fd[0] == '.' or not os.path.isdir(fd + dir):
                                        continue
                                n = '%s/%s' % (user, dir)
                                options.append((n, n))
        return options

def move_fotos_list_events():
        events = list(map(os.path.basename, glob('%s/20*' % PHOTOS_DIR)))
        events.sort(reverse=True)
        return map(lambda x: (x, x), events)

class CreateEventForm(forms.Form):
        date = forms.DateField(label='Datum', initial=date.today)
        humanName = forms.CharField(label='Naam voor mensen')
        fullHumanName = forms.CharField(label='Volledige naam voor mensen')
        name = forms.RegexField(label='Naam voor computers', 
                        regex=r'^[a-z0-9-]{3,64}$')

        date.widget.attrs['onblur'] = 'createFullHumanname();'
        humanName.widget.attrs['onblur'] = 'createTechName(); createFullHumanname();'

class MoveFotosForm(forms.Form):
        move_src = forms.ChoiceField(label='Verplaats', choices=move_fotos_scan_userdirs())
        move_dst = forms.ChoiceField(label='naar', choices=move_fotos_list_events())
