from django.http import Http404
from django.template import RequestContext
from kn.leden.models import KnGroup, KnUser
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def knuser_detail(request, name):
	try:
		user = KnUser.objects.select_related('seat_set',
				'groups').get(username=name)
	except KnUser.DoesNotExist:
		raise Http404
	seats = list(user.seat_set.select_related('group').all())
	seats.sort(lambda x,y: cmp(x.group.humanName, y.group.humanName))
	comms = map(lambda x: x.kngroup, user.groups.all())
	comms.sort(lambda x,y: cmp(x.humanName, y.humanName))
	return render_to_response('leden/knuser_detail.html',
			{'object': user,
			 'seats': seats,
			 'comms': comms},
			context_instance=RequestContext(request))

@login_required
def kngroup_detail(request, name):
	try:
		group = KnGroup.objects.select_related('seat_set',
				'user_set').order_by('humanName').get(name=name)
	except KnGroup.DoesNotExist:
		raise Http404
	otherMembers = list()
	subGroups = list(group.kngroup_set.order_by('humanName').all())
	seats = list(group.seat_set.order_by('humanName').all())
	seat_ids = frozenset(map(lambda x: x.user_id, seats))
	for user in group.user_set.select_related('knuser'
			).order_by('first_name').all():
		if user.id in seat_ids:
			continue
		otherMembers.append(user)
	return render_to_response('leden/kngroup_detail.html',
			{'object': group,
		 	 'seats': seats,
			 'subGroups': subGroups,
			 'otherMembers': otherMembers},
			context_instance=RequestContext(request))
