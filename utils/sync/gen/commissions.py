from common import *
from kn.leden.models import OldKnUser, OldKnGroup, OldSeat, Alias

def change_comm_membership(cname, desired):
	comm = OldKnGroup.objects.get(name=cname)
	accounted = set()
	seen = set()
	for user in comm.user_set.all():
		accounted.add(user.username)
	for user in desired:
		seen.add(user.username)
		if not user.username in accounted:
			user.groups.add(comm)
			user.save()
			print "notice Added %s to %s" % (user.username, comm)
	for unacc in accounted - seen:
		OldKnUser.objects.get(username=unacc).groups.remove(comm)
		print "notice Removed %s from %s" % (unacc, comm)


def sync_commissions():
	mg = OldKnGroup.objects.get(name=MEMBER_GROUP)
	leden = set()
	eerstejaars = set()
	for user in OldKnUser.objects.all():
		if (not user.groups.filter(pk=mg.pk) and
			user.is_active):
			print "notice %s not in %s, deactivated" % (
					user.username, MEMBER_GROUP)
			user.is_active = False
			user.save()
		groupNames = map(lambda x: x.name, user.groups.all())
		if any(map(lambda x: (x[:5] == 'leden' and x != 'leden'),
				groupNames)):
			leden.add(user)
			if not any(map(lambda x: (x[:5] == 'leden'
					and x != 'leden'
					and x != MEMBER_GROUP), groupNames)):
				eerstejaars.add(user)
	change_comm_membership('leden', leden)
	change_comm_membership('eersteJaars', eerstejaars)
	change_comm_membership('leden-oud',
		set(OldKnGroup.objects.get(name='leden').user_set.all()) -
		set(mg.user_set.all()))
	change_comm_membership('mannen',
		OldKnUser.objects.filter(gender='m'))
	change_comm_membership('vrouwen',
		OldKnUser.objects.filter(gender='v'))
	change_comm_membership('hoofden',
		map(lambda x: x.user,
			OldSeat.objects.select_related('user').filter(
				name='hoofd')) +
		map(lambda x: x.user,
			OldSeat.objects.select_related('user').filter(
				group=OldKnGroup.objects.get(name='hoofden'))))

