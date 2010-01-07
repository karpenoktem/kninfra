from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.models import Group
from kn.subscriptions.models import Event, EventSubscription
from kn.leden.models import OldKnUser, OldKnGroup
from django.http import Http404
from django.core.mail import EmailMessage

@login_required
def event_detail(request, name):
	try:
		event = Event.objects.get(name=name)
	except Event.DoesNotExist:
		raise Http404
	try:
		subscription = EventSubscription.objects.get(
				event=event, user=request.user)
	except EventSubscription.DoesNotExist:
		subscription = None
	if subscription:
		if subscription.debit > 0:
			request.user.message_set.create(message=(
				"Je bent al aangemeld, maar moet nog wel %s"+
				" euro betalen.") % subscription.debit)
		else:
			request.user.message_set.create(
				message="Je bent aangemeld en je"+\
						" betaling is verwerkt!")
	elif request.method == 'POST':
		subscription = EventSubscription(
			event=event,
			user=OldKnUser.objects.get(
				username=request.user.username),
			debit=event.cost)
		subscription.save()
		full_owner_address = '%s <%s>' % (
				event.owner.humanName,
				event.owner.primary_email)
		email = EmailMessage(
				"Aanmelding %s" % event.humanName,
				 event.mailBody % {
					'firstName': request.user.first_name},
				'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
				[request.user.oldknuser.primary_email],
				[event.owner.primary_email],
				headers={
					'Cc': full_owner_address,
					'Reply-To': full_owner_address})
		email.send()
		request.user.message_set.create(
			message="Je bent aangemeld en moet "+\
					"nu %s euro betalen" % event.cost)
	try:
		request.user.groups.get(name=event.owner)
		# An exception would have been triggered,
		# if we weren't in the group as specified by owner
		subscrlist = EventSubscription.objects.filter(event=event)
		subscrcount_debit = subscrlist.exclude(debit=0).count()
	except Group.DoesNotExist:
		subscrlist = None
	return render_to_response('subscriptions/event_detail.html',
			{'object': event,
			 'subscrlist': subscrlist,
			 'subscrcount_debit': subscrcount_debit,
			 'subscription': subscription},
			context_instance=RequestContext(request))
