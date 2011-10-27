import decimal
import datetime
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from kn.fotos.forms import CreateEventForm, MoveFotosForm
import kn.leden.entities as Es
from kn.leden.mongo import _id
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from glob import glob
from os.path import basename

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
                        print giedo.fotoadmin_create_event(cd['date'].__str__(),
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
        if request.method == 'POST':
                form = MoveFotosForm(request.POST)
                if form.is_valid():
                        cd = form.cleaned_data
                        (user, dir) = cd['move_src'].split('/')
                        print giedo.fotoadmin_move_fotos(cd['move_dst'], user, dir)
        else:
                form = MoveFotosForm()
        return render_to_response('fotos/admin/move.html',
                        {'form': form},
                        context_instance=RequestContext(request))
