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
    offset = int(data.get('offset', 0))
    count = int(data.get('count', 12))
    o = fEs.by_path(data['path'])
    if o is None:
        return {'error': 'Object not found'}
    cs = o.list(request.user if request.user.is_authenticated() else None,
                    offset, count)
    ret_cs = []
    for c in cs:
        entry = {'type': c._type,
                 'thumbnail': c.get_thumbnail_url(),
                 'thumbnail2x': c.get_thumbnail2x_url(),
                 'path': c.full_path,
                 'title': c.title}
        if c._type == 'foto':
            entry['large'] = c.get_cache_url('large')
            entry['large2x'] = c.get_cache_url('large2x')
            entry['full'] = c.get_cache_url('full')
        ret_cs.append(entry)
    return {'children': ret_cs}

ACTION_HANDLER_MAP = {
        'list': _list,
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
