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
            entry['largeSize'] = child.get_cache_meta('large').get('size')
            if entry['largeSize'] is None:
                size2x = child.get_cache_meta('large2x').get('size')
                if size2x: entry['largeSize'] = [x/2 for x in size2x]
            entry['thumbnailSize'] = child.get_cache_meta('thumb').get('size')
            if entry['thumbnailSize'] is None:
                size2x = child.get_cache_meta('thumb2x').get('size')
                if size2x: entry['thumbnailSize'] = [x/2 for x in size2x]
        json_children.append(entry)

    current_album = album
    json_parents = {}
    while current_album.full_path:
        json_parents[current_album.full_path] = current_album.title
        current_album = current_album.get_parent()

    return {'children': json_children,
            'parents': json_parents}

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
