from common import *
from kn.leden.models import OldKnUser, OldKnGroup, OldSeat, Alias

seat_comm_lut = None

def seat_users_for(cname):
	global seat_comm_lut
	if seat_comm_lut is None:
		seat_comm_lut = dict()
		for s in OldSeat.objects.all():
			if not s.group.name in seat_comm_lut:
				seat_comm_lut[s.group.name] = set()
			seat_comm_lut[s.group.name].add(s.user)
	return seat_comm_lut[cname] if cname in seat_comm_lut else set()

def change_comm_membership(cname, desired):
	desired = frozenset(desired).union(seat_users_for(cname))
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
	on_leden = set()
	leden = set(map(lambda x: x.oldknuser, mg.user_set.all()))
	eerstejaars = set()
	for user in OldKnUser.objects.all():
		if (not user.groups.filter(pk=mg.pk) and
			user.is_active and not user.force_is_active):
			print "notice %s not in %s, deactivated" % (
					user.username, MEMBER_GROUP)
			user.is_active = False
			user.save()
		groupNames = map(lambda x: x.name, user.groups.all())
		if any(map(lambda x: (x[:5] == 'leden' and x != 'leden'),
				groupNames)):
			on_leden.add(user)
			if not any(map(lambda x: (x[:5] == 'leden'
					and x != 'leden'
					and x != MEMBER_GROUP), groupNames)):
				eerstejaars.add(user)
	change_comm_membership('leden', leden)
	change_comm_membership('aan',
		filter(lambda x: x.in_aan, leden))
	change_comm_membership('naast',
		filter(lambda x: x.in_naast, leden))
	change_comm_membership('eerstejaars', eerstejaars)
	change_comm_membership('leden-oud',
		on_leden - leden)
	change_comm_membership('oud',
		filter(lambda x: x.in_oud, on_leden - leden))
	change_comm_membership('incasso',
		filter(lambda x: x.got_incasso, leden))
	change_comm_membership('geen-incasso',
		filter(lambda x: not x.got_incasso, leden))
	change_comm_membership('mannen',
		filter(lambda x: x.gender == 'm', leden))
	change_comm_membership('vrouwen',
		filter(lambda x: x.gender == 'v', leden))
	change_comm_membership('hoofden',
		map(lambda x: x.user,
			OldSeat.objects.select_related('user').filter(
				name='hoofd')) +
		map(lambda x: x.user,
			OldSeat.objects.select_related('user').filter(
				group=OldKnGroup.objects.get(name='hoofden'))))
	for group in OldKnGroup.objects.all():
		change_comm_membership(group.name, group.user_set.all())
