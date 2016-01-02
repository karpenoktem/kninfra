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

def album_parents_json(album):
    json_parents = {}
    current_album = album
    while current_album is not None:
        json_parents[current_album.full_path] = current_album.title
        current_album = current_album.get_parent()

    return json_parents

def album_json(album, user):
    if not album.may_view(user):
        raise PermissionDenied

    children, people = entities_json(album.list(user), user)

    return {'children': children,
            'parents': album_parents_json(album),
            'visibility': album.visibility[0],
            'people': people}

def entities_json(children, user):
    '''
    Return the JSON dictionary for this entity.
    '''

    entries = []
    people = {}
    for child in children:
        entry = {'type': child._type,
                 'path': child.full_path,
                 'name': child.name,
                 'title': child.title,
                 'rotation': child.rotation}

        if fEs.is_admin(user):
            entry['visibility'] = child.visibility[0]

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
                    people[str(tag.name)] = unicode(tag.humanName)
                entry['tags'] = tags

        entries.append(entry)

    return entries, people

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
    user = request.user if request.user.is_authenticated() else None
    if not fEs.is_admin(user):
        raise PermissionDenied

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

    result = {'Ok': True}

    if entity._type == 'foto':
        if 'rotation' not in data:
            return {'error': 'missing rotation attribute'}
        if not isinstance(data['rotation'], int):
            return {'error': 'rotation should be a number'}
        rotation = data['rotation']
        if rotation not in [0, 90, 180, 270]:
            return {'error': 'rotation is not valid'}
        entity.set_rotation(rotation, save=False)

        result['largeSize'] = entity.get_cache_size('large')

    if entity._type in ['foto', 'video']:
        if 'description' not in data:
            return {'error': 'missing description attribute'}
        if not isinstance(data['description'], basestring):
            return {'error': 'description should be a string'}
        description = data['description'].strip()
        if not description:
            description = None
        entity.set_description(description, save=False)

        if 'tags' not in data:
            return {'error': 'missing tags attribute'}
        if not isinstance(data['tags'], list):
            return {'error': 'tags should be a list'}
        if not all(isinstance(n, basestring) for n in data['tags']):
            return {'error': 'tags may only contain strings'}
        tags = data['tags']
        entity.set_tags(tags, save=True)

        result['thumbnailSize'] = entity.get_cache_size('thumb')

    entity.set_title(title, save=False)

    # save changes in one batch
    entity.save()
    # except for visibility which is much harder to save in the same batch
    if entity.is_root:
        return result
    entity.update_visibility([visibility])
    return result

def _remove(data, request):
    user = request.user if request.user.is_authenticated() else None
    if not fEs.is_admin(user):
        raise PermissionDenied

    foto = entity_from_request(data)
    if isinstance(foto, basestring):
        return {'error': foto}

    # No visibility equals removal.
    foto.update_visibility([])

    return {'Ok': True}

def _search(data, request):
    album = entity_from_request(data)
    if isinstance(album, basestring):
        return {'error': album}

    user = request.user if request.user.is_authenticated() else None
    if not album.may_view(user):
        raise PermissionDenied

    if 'q' not in data:
        return {'error': 'missing q attribute'}
    if not isinstance(data['q'], basestring):
        return {'error': 'q should be string'}
    q = data['q'].strip()
    if not q:
        return {'error': 'q should not be empty'}

    results, people = entities_json(album.search(q, user), user)
    return {'results': results,
            'people': people}

ACTION_HANDLER_MAP = {
        'list': _list,
        'set-metadata': _set_metadata,
        'remove': _remove,
        'search': _search,
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
