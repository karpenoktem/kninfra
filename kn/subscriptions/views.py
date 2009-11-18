from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.contrib.auth.models import Group
from kn.subscriptions.models import Event, EventSubscription
from kn.leden.models import OldKnUser, OldKnGroup
from django.http import Http404

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
				"Je bent al aangemeld, maar moet nog wel €%s"+
				" euro betalen.")) % subscription.debit
		else:
			request.user.message_set.create(
					message="Je bent aangemeld!"
	elif request.method == 'POST':
		subscription = EventSubscription(
			event=event,
			user=OldKnUser.objects.get(
				username=request.user.username),
			debit=event.cost)
		subscription.save()
		request.user.message_set.create(message="Je bent aangemeld!")
	try:
		request.user.groups.get(name=event.owner)
		# An exception would have been triggered,
		# if we weren't in the group as specified by owner
		subscrlist = EventSubscription.objects.filter(event=event)
	except Group.DoesNotExist:
		subscrlist = None
	return render_to_response('leden/event_detail.html',
			{'object': event,
			 'message': message, 
			 'subscrlist': subscrlist, 
			 'subscription': subscription},
			context_instance=RequestContext(request))
