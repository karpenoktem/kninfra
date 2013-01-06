# vim: et:sta:bs=2:sw=4:
import decimal
import datetime

from markdown import markdown

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group
import kn.subscriptions.entities as subscr_Es
from kn.subscriptions.forms import get_add_event_form
import kn.leden.entities as Es
from kn.leden.mongo import _id
from kn.leden.date import date_to_dt
from kn.base.http import JsonHttpResponse
from django.http import Http404, HttpResponseRedirect
from django.core.mail import EmailMessage
from django.core.exceptions import PermissionDenied

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
    subscription = event.get_subscription_of(request.user)
    # What are our permissions?
    has_read_access = event.has_read_access(request.user)
    has_write_access = event.has_write_access(request.user)
    may_subscribe_others = (has_write_access or
                        event.everyone_can_subscribe_others)
    # Are we subscribing someone else?
    if (request.method == 'POST' and event.is_open and 'who' in request.POST
            and request.POST['who'] != str(request.user.id)):
        other_subscription = event.get_subscription_of(request.POST['who'])
        # Are we allowed to subscribe others?
        if not may_subscribe_others:
            raise PermissionDenied
        # Is the other already subscribed
        if other_subscription is not None:
            request.user.push_message("%s is al aangemeld" % (
                Es.by_id(request.POST['who']).full_name))
        else:
            # Find the user to subscribe
            user = Es.by_id(request.POST['who'])
            if not user or not user.is_user:
                raise Http404
            notes = request.POST['notes']
            other_subscription = subscr_Es.Subscription({
                'event': event._id,
                'user': _id(user),
                'date': datetime.datetime.now(),
                'debit': str(event.cost),
                'subscribedBy_notes': notes,
                'confirmed': False,
                'subscribedBy': _id(request.user)})
            other_subscription.save()
            email = EmailMessage(
                    "Bevestig je aanmelding voor %s" % event.humanName,
                     event.subscribedByOtherMailBody % {
                        'firstName': user.first_name,
                        'by_firstName': request.user.first_name,
                        'by_notes': notes,
                        'eventName': event.humanName,
                        'confirmationLink': ("http://karpenoktem.nl%s" %
                                reverse('event-detail', args=(event.name,))),
                        'owner': event.owner.humanName},
                    'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
                    [user.canonical_full_email],
                    [event.owner.canonical_full_email,
                     request.user.canonical_full_email],
                    headers={
                        'Cc': '%s, %s' % (event.owner.canonical_full_email,
                                        request.user.canonical_full_email),
                        'Reply-To': event.owner.canonical_full_email})
            email.send()
    if (subscription is None and request.method == 'POST'
            and event.is_open and ('who' not in request.POST
                or request.POST['who'] == str(request.user.id))):
        notes = request.POST['notes']
        subscription = subscr_Es.Subscription({
            'event': event._id,
            'user': request.user._id,
            'userNotes': notes,
            'date': datetime.datetime.now(),
            'debit': str(event.cost)})
        subscription.save()
        email = EmailMessage(
                "Aanmelding %s" % event.humanName,
                 event.mailBody % {
                    'firstName': request.user.first_name,
                    'eventName': event.humanName,
                    'owner': event.owner.humanName,
                    'notes': notes},
                'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
                [request.user.canonical_full_email],
                [event.owner.canonical_full_email],
                headers={
                    'Cc': event.owner.canonical_full_email,
                    'Reply-To': event.owner.canonical_full_email})
        email.send()
    subscrlist = tuple(event.get_subscriptions())
    ctx = {'object': event,
           'user': request.user,
           'subscription': subscription,
           'subscrlist': subscrlist,
           'subscrcount_debit': len([s for s in subscrlist
                            if s.debit != 0]),
           'subscrlist_count': len(subscrlist),
           'has_debit_access': event.has_debit_access(request.user),
           'may_subscribe_others': may_subscribe_others,
           'has_read_access': has_read_access,
           'has_write_access': has_write_access}
    if may_subscribe_others:
        ctx['users'] = sorted(Es.by_name('leden').get_members(),
                        lambda x,y: cmp(unicode(x.humanName),
                            unicode(y.humanName)))
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

def _api_confirm_subscription(request):
    if not 'id' in request.REQUEST:
        return JsonHttpResponse({'error': 'missing argument'})
    # Find the event and subscription
    event = subscr_Es.event_by_id(request.REQUEST['id'])
    if event is None:
        return JsonHttpResponse({'error': 'event not found'})
    subscription = event.get_subscription_of(request.user)
    if subscription is None:
        return JsonHttpResponse({'error': 'subscription not found'})
    # Confirm, if not confirmed already
    if subscription.confirmed:
        return JsonHttpResponse({'error': 'already confirmed'})
    subscription.confirmed = True
    subscription.dateConfirmed = datetime.datetime.now()
    subscription.save()
    return JsonHttpResponse({'success': True})

def _api_get_email_addresses(request):
    if not 'id' in request.REQUEST:
        return JsonHttpResponse({'error': 'missing arguments'})
    event = subscr_Es.event_by_id(request.REQUEST['id'])
    if not event:
        raise Http404
    if (not event.has_public_subscriptions and
            not event.has_read_access(request.user) and
            not event.has_debit_access(request.user)):
        raise PermissionDenied
    # XXX We can optimize this query
    return JsonHttpResponse({
            'success': True,
            'addresses': [s.user.canonical_full_email
                    for s in event.get_subscriptions()]})

def _api_change_debit(request):
    if not 'debit' in request.REQUEST or not 'id' in request.REQUEST:
        return JsonHttpResponse({'error': 'missing arguments'})
    subscr = subscr_Es.subscription_by_id(request.REQUEST['id'])
    if not subscr:
        raise Http404
    try:
        d = decimal.Decimal(request.REQUEST['debit'])
    except decimal.InvalidOperation:
        return JsonHttpResponse({'error': 'not a decimal'})
    event = subscr.event
    if not event.has_debit_access(request.user):
        raise PermissionDenied
    subscr.debit = d
    subscr.save()
    return JsonHttpResponse({'success': True})

@login_required
def api(request):
    action = request.REQUEST.get('action')
    if action == 'change-debit':
        return _api_change_debit(request)
    elif action == 'get-email-addresses':
        return _api_get_email_addresses(request)
    elif action == 'close-event':
        return _api_close_event(request)
    elif action == 'confirm-subscription':
        return _api_confirm_subscription(request)
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
                not _id(e.owner) == request.user.id:
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
            if not superuser and not name.startswith(prefix):
                name = prefix + name
            d = {
                'date': date_to_dt(fd['date']),
                'owner': _id(fd['owner']),
                'description': fd['description'],
                'description_html': markdown(fd['description'],
                    safe_mode="escape"),
                'mailBody': fd['mailBody'],
                'subscribedByOtherMailBody': fd['subscribedByOtherMailBody'],
                'confirmationMailBody': fd['confirmationMailBody'],
                'everyone_can_subscribe_others':
                        fd['everyone_can_subscribe_others'],
                'has_public_subscriptions': fd['has_public_subscriptions'],
                'humanName': fd['humanName'],
                'createdBy': request.user._id,
                'name': name,
                'cost': str(fd['cost']),
                'is_open': True,
                'is_official': superuser}
            if edit is None:
                e = subscr_Es.Event(d)
            else:
                e._data.update(d)
            e.save()
            act = 'bewerkt' if edit else 'aangemaakt'
            EmailMessage(
                    "Activiteit %s %s door %s" % (fd['humanName'], act,
                        unicode(request.user.humanName)),
                    "%s heeft een activiteit %s:\n\n"\
                    "    http://karpenoktem.nl%s" %
                    (unicode(request.user.humanName), act,
                        reverse('event-detail', args=(e.name,))),
                    'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
                    ['secretariaat@karpenoktem.nl']).send()
            return HttpResponseRedirect(reverse('event-detail', args=(e.name,)))
    elif edit is None:
        form = AddEventForm()
    else:
        d = e._data
        form = AddEventForm(d)
    ctx = {'form': form}
    return render_to_response('subscriptions/event_new_or_edit.html', ctx,
            context_instance=RequestContext(request))
