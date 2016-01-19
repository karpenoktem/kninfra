
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
from django.http import Http404, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.contrib import messages

from kn.base.mail import render_then_email
from kn.base.http import JsonHttpResponse
import kn.utils.markdown
import kn.leden.entities as Es
from kn.leden.mongo import _id
from kn.leden.date import date_to_dt
import kn.subscriptions.entities as subscr_Es
from kn.subscriptions.forms import get_add_event_form

@login_required
def event_list(request):
    open_events, closed_events, open_leden_events, \
                closed_leden_events = [],[],[],[]
    for e in reversed(tuple(subscr_Es.all_events())):
        if e.is_open:
            if e.is_official:
                open_events.append(e)
            else:
                open_leden_events.append(e)
        else:
            if e.is_official:
                closed_events.append(e)
            else:
                closed_leden_events.append(e)
    return render_to_response('subscriptions/event_list.html',
            {'open_events': open_events,
             'closed_events': closed_events,
             'open_leden_events': open_leden_events,
             'closed_leden_events': closed_leden_events},
            context_instance=RequestContext(request))

@login_required
def event_detail(request, name):
    # First, find the event.
    event = subscr_Es.event_by_name(name)
    if event is None:
        raise Http404
    # Has the user already subscribed?
    subscription = event.get_subscription(request.user)
    # What are our permissions?
    has_read_access = event.has_read_access(request.user)
    has_write_access = event.has_write_access(request.user)
    if request.method == 'POST' and 'subscribe' in request.POST:
        if not event.can_subscribe:
            raise PermissionDenied
        if subscription is not None and subscription.subscribed:
            messages.error(request, "Je bent al aangemeld")
        else:
            notes = request.POST['notes']
            subscription = event.subscribe(request.user, notes)
        return HttpResponseRedirect(reverse('event-detail',
                                            args=(event.name,)))
    elif request.method == 'POST' and 'invite' in request.POST:
        if not event.is_open:
            raise PermissionDenied
        # Find the other user
        user = Es.by_id(request.POST['who'])
        if not user or not user.is_user:
            raise Http404
        # Is the other already subscribed?
        if event.get_subscription(user) is not None:
            messages.error(request, "%s is al aangemeld" % user.full_name)
        else:
            notes = request.POST['notes']
            other_subscription = event.invite(user, notes, request.user)
        return HttpResponseRedirect(reverse('event-detail',
                                            args=(event.name,)))

    users = filter(lambda u: event.get_subscription(u) is None and \
                             u != request.user,
                   Es.by_name('leden').get_members())
    users.sort(key=lambda u: unicode(u.humanName))
    subscriptions = event.subscriptions
    subscriptions.sort(key=lambda s: s.date)
    invitations = event.invitations
    invitations.sort(key=lambda i: i.date)

    ctx = {'object': event,
           'user': request.user,
           'users': users,
           'subscription': subscription,
           'subscriptions': subscriptions,
           'invitations': invitations,
           'has_read_access': has_read_access,
           'has_write_access': has_write_access}
    return render_to_response('subscriptions/event_detail.html', ctx,
            context_instance=RequestContext(request))

def _api_close_event(request):
    if not 'id' in request.REQUEST:
        return JsonHttpResponse({'error': 'missing argument'})
    e = subscr_Es.event_by_id(request.REQUEST['id'])
    if not e:
        raise Http404
    if not e.has_write_access(request.user):
        raise PermissionDenied
    e.is_open = False
    e.save()
    return JsonHttpResponse({'success': True})

def _api_get_email_addresses(request):
    if not 'id' in request.REQUEST:
        return JsonHttpResponse({'error': 'missing arguments'})
    event = subscr_Es.event_by_id(request.REQUEST['id'])
    if not event:
        raise Http404
    if (not event.has_public_subscriptions and
            not event.has_read_access(request.user)):
        raise PermissionDenied
    # XXX We can optimize this query
    return JsonHttpResponse({
            'success': True,
            'addresses': [s.user.canonical_full_email
                    for s in event.subscriptions]})

@login_required
def api(request):
    action = request.REQUEST.get('action')
    if action == 'get-email-addresses':
        return _api_get_email_addresses(request)
    elif action == 'close-event':
        return _api_close_event(request)
    else:
        return JsonHttpResponse({'error': 'unknown action'})

@login_required
def event_new_or_edit(request, edit=None):
    superuser = 'secretariaat' in request.user.cached_groups_names
    if edit is not None:
        e = subscr_Es.event_by_name(edit)
        if e is None:
            raise Http404
        if not superuser and not request.user.is_related_with(e.owner) and \
                not _id(e.owner) == request.user._id:
            raise PermissionDenied
    AddEventForm = get_add_event_form(request.user, superuser)
    if request.method == 'POST':
        form = AddEventForm(request.POST)
        if form.is_valid():
            fd = form.cleaned_data
            if not superuser and not request.user.is_related_with(
                    fd['owner']) and not fd['owner'] == request.user.id:
                raise PermissionDenied
            name = fd['name']
            # If not secretariaat, then prefix name with the username
            if fd['owner'] == request.user.id:
                prefix = str(request.user.name) + '-'
            else:
                prefix = str(Es.by_id(fd['owner']).name) + '-'
            if (not superuser and not name.startswith(prefix) and (
                    edit is None or e.name != name)):
                name = prefix + name
            d = {
                'date': date_to_dt(fd['date']),
                'owner': _id(fd['owner']),
                'description': fd['description'],
                'description_html': kn.utils.markdown.parser.convert(
                                                fd['description']),
                'subscribedMailBody': fd['subscribedMailBody'],
                'invitedMailBody': fd['invitedMailBody'],
                'has_public_subscriptions': fd['has_public_subscriptions'],
                'humanName': fd['humanName'],
                'createdBy': request.user._id,
                'name': name,
                'cost': str(fd['cost']),
                'max_subscriptions': fd['max_subscriptions'],
                'is_official': superuser}
            if edit is None:
                d['is_open'] = True # default for new events
                e = subscr_Es.Event(d)
            else:
                e._data.update(d)
            e.save()
            render_then_email('subscriptions/' +
                    ('event-edited' if edit else 'new-event') + '.mail.txt',
                    Es.by_name('secretariaat').canonical_full_email, {
                        'event': e,
                        'user': request.user},
                    headers={
                        'In-Reply-To': e.messageId,
                        'References': e.messageId,
                    },
            )
            return HttpResponseRedirect(reverse('event-detail', args=(e.name,)))
    elif edit is None:
        form = AddEventForm()
    else:
        d = e._data
        form = AddEventForm(d)
    ctx = {'form': form,
           'edit': edit}
    return render_to_response('subscriptions/event_new_or_edit.html', ctx,
            context_instance=RequestContext(request))

# vim: et:sta:bs=2:sw=4:
