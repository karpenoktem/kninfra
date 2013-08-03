import datetime

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext

import kn.utils.markdown
import kn.events.entities as events_Es
from kn.events.forms import get_add_event_form
from kn.leden.date import date_to_dt
from kn.leden.mongo import _id

@login_required
def event_detail(request, name):
    event = events_Es.event_by_name(name)
    return render_to_response('events/event_detail.html',
                        {'event': event},
            context_instance=RequestContext(request))

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
def event_new_or_edit(request, edit=None):
    superuser = 'secretariaat' in request.user.cached_groups_names
    # If we are editing an existing event, fetch it!
    if edit is not None:
        e = events_Es.event_by_name(edit)
        if e is None:
            raise Http404
        if not superuser and not request.user.is_related_with(e.owner) and \
                not _id(e.owner) == request.user.id:
            raise PermissionDenied
    AddEventForm = get_add_event_form(request.user, superuser)
    # Has the user submitted the form?
    if request.method == 'POST':
        form = AddEventForm(request.POST)
        if form.is_valid():
            fd = form.cleaned_data
            if not superuser and not request.user.is_related_with(
                            fd['owner']) and not fd['owner'] == request.user.id:
                raise PermissionDenied
            d = {   'when': date_to_dt(fd['when']),
                    'name': fd['name'],
                    'humanName': fd['humanName'],
                    'owner': _id(fd['owner']),
                    'description': fd['description'],
                    'description_html': kn.utils.markdown.parser.convert(
                                                fd['description']),
                    'msg_subscribed': fd['msg_subscribed'],
                    'msg_subscribedBy': fd['msg_subscribedBy'],
                    'msg_confirmed': fd['msg_confirmed'],
                    'has_public_subscriptions': fd['has_public_subscriptions'],
                    'owner_can_subscribe_others': fd[
                                        'owner_can_subscribe_others'],
                    'anyone_can_subscribe_others': fd[
                                        'anyone_can_subscribe_others'],
                    'cost': str(fd['cost']),
                    'manually_closed': False}
            change = {
                    'type': 'update',
                    'by': _id(request.user),
                    'when': datetime.datetime.now()}
            if edit is None:
                d['changes'] = [change]
                e = events_Es.Event(d)
            else:
                e._data['changes'].append(change)
                e._data.update(d)
            e.save()
            return HttpResponseRedirect(reverse('event-detail', args=(e.name,)))
    elif edit is None:
        form = AddEventForm()
    else:
        d = e._data
        form = AddEventForm(d)
    ctx = {'form': form}
    return render_to_response('subscriptions/event_new_or_edit.html', ctx,
            context_instance=RequestContext(request))

# vim: et:sta:bs=2:sw=4:
