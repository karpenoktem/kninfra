import json

from django.contrib.auth.decorators import login_required

import kn.leden.entities as Es
from kn.leden.mongo import _id

@login_required
def view(request):
    data = json.loads(request.REQUEST.get('data', {}))
    action = data.get('action')
    handler = ACTION_HANDLER_MAP.get(action,
                    ACTION_HANDLER_MAP[None])
    return JsonHttpResponse(handler(data, request))

def no_such_action(data, request):
    return {'error': 'No such action'}

ACTION_HANDLER_MAP = {
        None: no_such_action,
        }

# vim: et:sta:bs=2:sw=4:
