import json

from django.contrib.auth.decorators import login_required

from kn.base.http import JsonHttpResponse
import kn.leden.entities as Es

@login_required
def view(request):
    data = json.loads(request.REQUEST.get('data', {}))
    action = data.get('action')
    handler = ACTION_HANDLER_MAP.get(action,
                    ACTION_HANDLER_MAP[None])
    return JsonHttpResponse(handler(data))

def no_such_action(data):
    return {'error': 'No such action'}

def entities_by_keyword(data):
    """ Wraps Es.by_keyword.  Finds the first 20 entities matching the given
        keyword.  Example:
        
          >> {action:"by_keyword", keyword: "giedo"}
          << [["4e6fcc85e60edf3dc0000270", "Giedo Jansen (giedo)"]]

        The return format is optimized for size and compatibility with
        jquery-ui.autocomplete """
    _type = data.get('type', None)
    if _type and not isinstance(_type, basestring):
        _type = None
    return [[e.id, "%s (%s)" % (e.humanName, e.name)]
                    for e in Es.by_keyword(data.get('keyword', ''),
                                           _type=_type)]


ACTION_HANDLER_MAP = {
        'entities_by_keyword': entities_by_keyword,
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
