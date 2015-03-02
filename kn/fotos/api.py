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

    people = {}

    children = album.list(user)
    json_children = []
    for child in children:
        entry = {'type': child._type,
                 'path': child.full_path,
                 'name': child.name,
                 'title': child.title}

        if child.description:
            entry['description'] = child.description;
        if child._type == 'foto':
            entry['largeSize'] = child.get_cache_size('large')
            entry['thumbnailSize'] = child.get_cache_size('thumb')
        elif child._type == 'album':
            album_foto = child.get_random_foto_for(user)
            if album_foto is not None:
                entry['thumbnailSize'] = album_foto.get_cache_size('thumb')
                entry['thumbnailPath'] = album_foto.full_path
        if child._type != 'album':
            tags = []
            tagged = child.get_tags()
            if tagged:
                for tag in tagged:
                    tags.append(str(tag.name))
                    people[str(tag.name)] = str(tag.humanName)
            entry['tags'] = tags

        json_children.append(entry)

    current_album = album
    json_parents = {}
    while current_album is not None:
        json_parents[current_album.full_path] = current_album.title
        current_album = current_album.get_parent()

    return {'children': json_children,
            'parents': json_parents,
            'visibility': album.visibility[0],
            'people': people}

def entity_from_request(data):
    if 'path' not in data:
        return 'Missing path attribute'
    if not isinstance(data['path'], basestring):
        return 'path should be string'
    entity = fEs.by_path(data['path'])
    if entity is None:
        return 'Object not found'
    return entity

def _list(data, request):
    album = entity_from_request(data)
    if isinstance(album, basestring):
        return {'error': album}
    user = request.user if request.user.is_authenticated() else None
    return album_json(album, user)

def _set_metadata(data, request):
    if 'title' not in data:
        return {'error': 'missing title attribute'}
    if not isinstance(data['title'], basestring):
        return {'error': 'title should be string'}
    title = data['title'].strip()
    if not title:
        title = None

    if 'visibility' not in data:
        return {'error': 'missing visibility attribute'}
    if data['visibility'] not in ['world', 'leden', 'hidden']:
        return {'error': 'visibility not valid'}
    visibility = data['visibility']

    entity = entity_from_request(data)
    if isinstance(entity, basestring):
        return {'error': entity}

    user = request.user if request.user.is_authenticated() else None
    if not fEs.is_admin(user):
        raise PermissionDenied

    entity.set_title(title)
    entity.update_visibility([visibility])
    return {'Ok': True}

ACTION_HANDLER_MAP = {
        'list': _list,
        'set-metadata': _set_metadata,
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
