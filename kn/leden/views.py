from django.http import Http404
from kn.leden.models import KnGroup
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def kngroup_detail(request, object_id):
	try:
		group = KnGroup.objects.select_related('seat_set',
				'user_set').get(id=object_id)
	except KnGroup.DoesNotExist:
		raise Http404
	otherMembers = list()
	seats = list(group.seat_set.all())
	seat_ids = frozenset(map(lambda x: x.user_id, seats))
	for user in group.user_set.select_related('knuser').all():
		if user.id in seat_ids:
			continue
		otherMembers.append(user)
	return render_to_response('leden/kngroup_detail.html',
			{'object': group,
		 	 'seats': seats,
			 'otherMembers': otherMembers})
