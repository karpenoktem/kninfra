from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import Group
import kn.subscriptions.entities as subscr_Es
import kn.leden.entities as Es
from django.http import Http404
from django.core.mail import EmailMessage

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
			request.user.push_message("Je bent aangemeld en je"+\
						" betaling is verwerkt!")
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
		request.user.push_message(
				"Je bent aangemeld en moet "+\
					"nu %s euro betalen" % event.cost)
	if request.user.is_related_with(event.owner):
		subscrlist = tuple(event.get_subscriptions())
		subscrcount_debit = len([s for s in subscrlist if s.debit != 0])
        else:
		subscrlist = None
		subscrcount_debit = None
	return render_to_response('subscriptions/event_detail.html',
			{'object': event,
			 'user': request.user,
			 'subscrlist': subscrlist,
			 'subscrcount_debit': subscrcount_debit,
			 'subscription': subscription},
			context_instance=RequestContext(request))
