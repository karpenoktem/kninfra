import decimal
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import Group
import kn.subscriptions.entities as subscr_Es
import kn.leden.entities as Es
from kn.leden.mongo import _id
from kn.base.http import JsonHttpResponse
from django.http import Http404
from django.core.mail import EmailMessage
from django.core.exceptions import PermissionDenied

@login_required
def event_list(request):
        events = tuple(subscr_Es.all_events())
        open_events = [e for e in reversed(events) if e.is_open]
        closed_events = [e for e in reversed(events) if not e.is_open]
	return render_to_response('subscriptions/event_list.html',
                        {'open_events': open_events,
                         'closed_events': closed_events},
			context_instance=RequestContext(request))


@login_required
def event_detail(request, name):
        event = subscr_Es.event_by_name(name)
        if event is None:
                raise Http404
        subscription = event.get_subscription_of(request.user)
	if subscription is not None:
		if subscription.debit > 0:
			request.user.push_message((
				"Je bent al aangemeld, maar moet nog wel %s"+
				" euro betalen.") % subscription.debit)
		else:
			request.user.push_message("Je bent aangemeld!")
	elif request.method == 'POST' and event.is_open:
                notes = request.POST['notes']
		subscription = subscr_Es.Subscription({
                        'event': event._id,
                        'user': request.user._id,
                        'userNotes': notes,
                        'debit': event.cost})
		subscription.save()
		full_owner_address = '%s <%s>' % (
				event.owner.humanName,
				event.owner.canonical_email)
		email = EmailMessage(
				"Aanmelding %s" % event.humanName,
				 event.mailBody % {
					'firstName': request.user.first_name,
                                        'notes': notes},
				'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
				[request.user.canonical_email],
				[event.owner.canonical_email],
				headers={
					'Cc': full_owner_address,
					'Reply-To': full_owner_address})
		email.send()
                if event.cost > 0:
                        request.user.push_message(
                                        "Je bent aangemeld en moet "+\
                                        "nu %s euro betalen" % event.cost)
                else:
                        request.user.push_message(
                                        "Je bent aangemeld")
        ctx = {'object': event,
               'user': request.user,
               'subscription': subscription,
               'has_debit_access': event.has_debit_access(request.user),
               'has_read_access': event.has_read_access(request.user),
               'has_write_access': event.has_write_access(request.user)}
        if event.has_read_access(request.user) or \
                        event.has_debit_access(request.user):
                subscrlist = tuple(event.get_subscriptions())
	        ctx.update({
                        'subscrlist': subscrlist,
                        'subscrcount_debit': len([s for s in subscrlist
                                                        if s.debit != 0]),
                        'subscrlist_count': len(subscrlist)})
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
        elif action == 'close-event':
                return _api_close_event(request)
        else:
                return JsonHttpResponse({'error': 'unknown action'})
