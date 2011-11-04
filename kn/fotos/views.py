# vim: et:sta:bs=2:sw=4:
from glob import glob
from os.path import basename

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from kn.fotos.forms import CreateEventForm, getMoveFotosForm
from kn.settings import PHOTOS_DIR
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
