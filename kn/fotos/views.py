from glob import glob
import os.path
from os.path import basename
from urllib import unquote

import MySQLdb
import Image

from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
from django.core.exceptions import PermissionDenied
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import EmptyPage
from django.core.urlresolvers import reverse
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, QueryDict

from kn.fotos.forms import CreateEventForm, getMoveFotosForm, list_events
from kn.settings import PHOTOS_DIR
from kn.leden import giedo

import kn.fotos.entities as fEs
import kn.leden.entities as Es
from kn.fotos.api import album_json, album_parents_json

def fotos(request, path=''):
    path = unquote(path)

    if any(k in request.GET for k in ['album', 'search_album', 'search_tag']):
        # redirect old URL
        path = request.GET.get('album', '')
        q = None
        if request.GET.get('search_album'):
            q = 'album:' + request.GET.get('search_album')
        if request.GET.get('search_tag'):
            q = 'tag:' + request.GET.get('search_tag')
        url = reverse('fotos', kwargs={'path':path})
        if q is not None:
            qs = QueryDict('', mutable=True)
            qs['q'] = q
            url += '?' + qs.urlencode()
        return redirect(url, permanent=True)

    album = fEs.by_path(path)
    if album is None:
        raise Http404
    user = request.user if request.user.is_authenticated() else None

    if not album.may_view(user) and user is None:
        # user is not logged in
        return redirect_to_login(request.get_full_path())

    if not album.may_view(user):
        # user is logged in, but may not view the album
        title = album.title
        if not title:
            title = album.name
        # respond with a nice error message
        response = render_to_response('fotos/fotos.html',
                  {'fotos': {'parents': album_parents_json(album)},
                   'error': 'permission-denied'},
                  context_instance=RequestContext(request))
        response.status_code = 403
        return response

    people = None
    if fEs.is_admin(user):
        # Get all members (now or in the past), and sort them first by whether they
        # are active (active members first) and then by their name.
        humanNames = {}
        active = []
        inactive = []
        for user in Es.users():
            humanNames[str(user.name)] = unicode(user.humanName)
            if user.is_active:
                active.append(str(user.name))
            else:
                inactive.append(str(user.name))
        active.sort()
        inactive.sort()
        people = []
        for name in active+inactive:
            people.append((name, humanNames[name]))

    fotos = album_json(album, user)
    return render_to_response('fotos/fotos.html',
             {'fotos': fotos,
              'fotos_admin': fEs.is_admin(user),
              'people': people},
             context_instance=RequestContext(request))

def cache(request, cache, path):
    path = unquote(path)
    if not cache in fEs.CACHE_TYPES:
        raise Http404
    entity = fEs.by_path(path)
    if entity is None:
        raise Http404
    user = request.user if request.user.is_authenticated() else None
    if not entity.may_view(user):
        if user is None:
            # user is not logged in
            return redirect_to_login(request.get_full_path())
        raise PermissionDenied
    entity.ensure_cached(cache)
    resp = HttpResponse(FileWrapper(open(entity.get_cache_path(cache))),
                            mimetype=entity.get_cache_mimetype(cache))
    resp['Content-Length'] = os.path.getsize(entity.get_cache_path(cache))
    return resp

def compat_view(request):
    path = request.GET.get('foto', '')
    name = None
    if '/' in path:
        path, name = path.rsplit('/', 1)
    return redirect('fotos', path=path+'#'+name, permanent=True)

def compat_foto(request):
    path = request.GET.get('foto', '')
    return redirect('fotos-cache', cache='full', path=path, permanent=True)

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
    return render_to_response('fotos/admin/create.html',
            {'form': form, 'events': list_events()},
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
