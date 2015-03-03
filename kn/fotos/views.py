from glob import glob
import os.path
from os.path import basename
from urllib import unquote

import MySQLdb
import Image

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import EmptyPage
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse

from kn.fotos.forms import CreateEventForm, getMoveFotosForm
from kn.settings import PHOTOS_DIR
from kn.leden import giedo

import kn.fotos.entities as fEs
from kn.fotos.api import album_json

def fotos(request, path=''):
    album = fEs.by_path(path)
    if album is None:
        raise Http404
    user = request.user if request.user.is_authenticated() else None

    fotos = album_json(album, user)
    return render_to_response('fotos/fotos.html',
             {'fotos': fotos,
              'fotos_admin': fEs.is_admin(user)},
             context_instance=RequestContext(request))

def cache(request, cache, path):
    path = unquote(path)
    if not cache in fEs.CACHE_TYPES:
        raise Http404
    entity = fEs.by_path(path)
    if entity is None:
        raise Http404
    if not entity.may_view(request.user if request.user.is_authenticated()
                        else None):
        raise PermissionDenied
    entity.ensure_cached(cache)
    resp = HttpResponse(FileWrapper(open(entity.get_cache_path(cache))),
                            mimetype=entity.get_cache_mimetype(cache))
    resp['Content-Length'] = os.path.getsize(entity.get_cache_path(cache))
    return resp

@login_required
def fotoadmin_create_event(request):
    if not fEs.is_admin(request.user):
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
    if not fEs.is_admin(request.user):
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

# vim: et:sta:bs=2:sw=4:
