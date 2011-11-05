# vim: et:sta:bs=2:sw=4:
from glob import glob
from os.path import basename

import MySQLdb
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from kn.fotos.forms import CreateEventForm, getMoveFotosForm
from kn.settings import PHOTOS_DIR, PHOTOS_MYSQL_SECRET
from kn.leden import giedo

@login_required
def fotoadmin_create_event(request):
    if not request.user.cached_groups_names & set(['fotocie', 'webcie']):
        raise PermissionDenied
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            giedo.fotoadmin_create_event(str(cd['date']),
                    cd['name'], cd['fullHumanName'])
    else:
        form = CreateEventForm()
    events = list(map(basename, glob('%s/20*' % PHOTOS_DIR)))
    events.sort(reverse=True)
    return render_to_response('fotos/admin/create.html',
            {'form': form, 'events': events},
             context_instance=RequestContext(request))

@login_required
def fotoadmin_move(request):
    if not request.user.cached_groups_names & set(['fotocie', 'webcie']):
        raise PermissionDenied
    MoveFotosForm = getMoveFotosForm()
    if request.method == 'POST':
        form = MoveFotosForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            (user, dir) = cd['move_src'].split('/')
            giedo.fotoadmin_move_fotos(cd['move_dst'], user, dir)
    else:
        form = MoveFotosForm()
    return render_to_response('fotos/admin/move.html',
            {'form': form},
             context_instance=RequestContext(request))

@login_required
def fotoadmin_status(request):
    if not request.user.cached_groups_names & set(['fotocie', 'webcie']):
        raise PermissionDenied
    creds = PHOTOS_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2], db=creds[3])
    c = dc.cursor()
    c.execute("SELECT path, name, cached FROM fa_photos WHERE ((NOT FIND_IN_SET('thumb', cached) OR NOT FIND_IN_SET('large', cached)) OR FIND_IN_SET('invalidated', cached)) AND visibility IN('hidden', 'leden', 'world')")
    photos = list()
    for row in c.fetchall():
        cached = row[2].split(',')
        photos.append({
            'photo': row[0] + row[1],
            'thumb': 'thumb' in cached,
            'large': 'large' in cached,
            'invalidated': 'invalidated' in cached,
            })
    c.close()
    dc.close()
    return render_to_response('fotos/admin/status.html',
            {'photos': photos},
             context_instance=RequestContext(request))
