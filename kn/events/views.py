from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext

import kn.events.entities as events_Es

@login_required
def event_detail(request):
    pass

@login_required
def event_list(request):
    open_events, closed_events = [], []
    for e in events_Es.all_events():
        if e.is_open:
            open_events.append(e)
        else:
            closed_events.append(e)
    return render_to_response('events/event_list.html',
            {'open_events': open_events,
             'closed_events': closed_events},
            context_instance=RequestContext(request))

@login_required
def api(request):
    pass

# vim: et:sta:bs=2:sw=4:
