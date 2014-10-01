import json

import kn.fotos.entities as fEs
from kn.base.http import JsonHttpResponse

def view(request):
    data = json.loads(request.REQUEST.get('data', {}))
    action = data.get('action')
    handler = ACTION_HANDLER_MAP.get(action,
                    ACTION_HANDLER_MAP[None])
    return JsonHttpResponse(handler(data, request))

def no_such_action(data, request):
    return {'error': 'No such action'}

def _list(data, request):
    if 'path' not in data:
        return {'error': 'Missing path attribute'}
    if not isinstance(data['path'], basestring):
        return {'error': 'path should be string'}
    o = fEs.by_path(data['path'])
    if o is None:
        return {'error': 'Object not found'}
    cs = o.list(request.user if request.user.is_authenticated() else None)
    ret_cs = []
    for c in cs:
        entry = {'type': c._type,
                 'path': c.full_path,
                 'name': c.name,
                 'title': c.title}
        if c._type == 'foto':
            entry['largeSize'] = c.get_cache_meta('large').get('size')
            if entry['largeSize'] is None:
                size2x = c.get_cache_meta('large2x').get('size')
                if size2x: entry['largeSize'] = [x/2 for x in size2x]
            entry['thumbnailSize'] = c.get_cache_meta('thumb').get('size')
            if entry['thumbnailSize'] is None:
                size2x = c.get_cache_meta('thumb2x').get('size')
                if size2x: entry['thumbnailSize'] = [x/2 for x in size2x]
        ret_cs.append(entry)
    return {'children': ret_cs}

ACTION_HANDLER_MAP = {
        'list': _list,
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
