import json

import kn.fotos.entities as fEs
from kn.base.http import JsonHttpResponse
from django.core.exceptions import PermissionDenied

def view(request):
    data = json.loads(request.REQUEST.get('data', {}))
    action = data.get('action')
    handler = ACTION_HANDLER_MAP.get(action,
                    ACTION_HANDLER_MAP[None])
    return JsonHttpResponse(handler(data, request))

def no_such_action(data, request):
    return {'error': 'No such action'}

def album_json(album, user):
    if not album.may_view(user):
        raise PermissionDenied
    children = album.list(user)
    json_children = []
    for child in children:
        entry = {'type': child._type,
                 'path': child.full_path,
                 'name': child.name,
                 'title': child.title}
        if child._type == 'foto':
            entry['largeSize'] = child.get_cache_size('large')
            entry['thumbnailSize'] = child.get_cache_size('thumb')
        elif child._type == 'album':
            album_foto = child.get_random_foto_for(user)
            entry['thumbnailSize'] = album_foto.get_cache_size('thumb')
            entry['thumbnailPath'] = album_foto.full_path
        json_children.append(entry)
    return {'children': json_children}

def _list(data, request):
    if 'path' not in data:
        return {'error': 'Missing path attribute'}
    if not isinstance(data['path'], basestring):
        return {'error': 'path should be string'}
    o = fEs.by_path(data['path'])
    if o is None:
        return {'error': 'Object not found'}
    user = request.user if request.user.is_authenticated() else None
    return album_json(o, user)

ACTION_HANDLER_MAP = {
        'list': _list,
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
