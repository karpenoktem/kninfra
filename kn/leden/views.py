from django.http import Http404
from django.template import RequestContext
from kn.leden.models import OldKnGroup, OldKnUser
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def oldknuser_detail(request, name):
	try:
		user = OldKnUser.objects.select_related('oldseat_set',
				'groups').get(username=name)
	except OldKnUser.DoesNotExist:
		raise Http404
	oldseats = list(user.oldseat_set.select_related('group').all())
	oldseats.sort(lambda x,y: cmp(x.humanName, y.humanName))
	comms = map(lambda x: x.oldkngroup, user.groups.all())
	comms.sort(lambda x,y: cmp(x.humanName, y.humanName))
	return render_to_response('leden/oldknuser_detail.html',
			{'object': user,
			 'oldseats': oldseats,
			 'comms': comms},
			context_instance=RequestContext(request))

@login_required
def oldkngroup_detail(request, name):
	try:
		group = OldKnGroup.objects.select_related('oldseat_set',
				'user_set').order_by('humanName').get(name=name)
	except OldKnGroup.DoesNotExist:
		raise Http404
	otherMembers = list()
	subGroups = list(group.oldkngroup_set.order_by('humanName').all())
	oldseats = list(group.oldseat_set.order_by('humanName').all())
	oldseat_ids = frozenset(map(lambda x: x.user_id, oldseats))
	for user in group.user_set.select_related('oldknuser'
			).order_by('first_name').all():
		if user.id in oldseat_ids:
			continue
		otherMembers.append(user)
	return render_to_response('leden/oldkngroup_detail.html',
			{'object': group,
		 	 'oldseats': oldseats,
			 'subGroups': subGroups,
			 'otherMembers': otherMembers},
			context_instance=RequestContext(request))
