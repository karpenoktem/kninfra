from common import *
from kn.leden.models import KnUser, KnGroup, Seat, Alias

def sync_commissions():
	mg = KnGroup.objects.get(name=MEMBER_GROUP)
	for user in KnUser.objects.all():
		if (not user.groups.filter(pk=mg.pk) and
			user.is_active):
			print "notice %s not in %s, deactivated" % (
					user.username, MEMBER_GROUP)
			user.is_active = False
			user.save()
	omg = KnGroup.objects.get(name='leden-oud')
	mgs = set(KnGroup.objects.filter(
			parent=KnGroup.objects.get(name='leden')))
	mgs.remove(omg)
	mgs.remove(mg)
	accounted = set()
	seen = set()
	for user in omg.user_set.all():
		accounted.add(user.username)
	for amg in mgs:
		for user in amg.user_set.all():
			seen.add(user.username)
	for user in mg.user_set.all():
		if user.username in seen:
			seen.remove(user.username)
	for user in accounted - seen:
		print "notice %s removes from leden-oud" % user
		KnUser.objects.get(username=user).groups.remove(omg)
	for user in seen - accounted:
		print "notice %s added to leden-oud" % user
		KnUser.objects.get(username=user).groups.add(omg)
	mannen = KnGroup.objects.get(name='mannen')
	accounted = set()
	seen = set()
	for user in mannen.user_set.all():
		accounted.add(user.username)
	for user in KnUser.objects.filter(gender='m'):
		seen.add(user.username)
		if not user.username in accounted:
			user.groups.add(mannen)
			user.save()
			print "notice Added %s to mannen" % user.username
	for unacc in accounted - seen:
		KnUser.objects.get(username=unacc).groups.remove(mannen)
		print "notice Removed %s from mannen" % unacc

	vrouwen = KnGroup.objects.get(name='vrouwen')
	accounted = set()
	seen = set()
	for user in vrouwen.user_set.all():
		accounted.add(user.username)
	for user in KnUser.objects.filter(gender='v'):
		seen.add(user.username)
		if not user.username in accounted:
			user.groups.add(vrouwen)
			user.save()
			print "notice Added %s to vrouwen" % user.username
	for unacc in accounted - seen:
		KnUser.objects.get(username=unacc).groups.remove(vrouwen)
		print "notice Removed %s from vrouwen" % unacc
	
	choofden = KnGroup.objects.get(name='hoofden')
	accounted = set()
	seen = set()
	for user in choofden.user_set.all():
		accounted.add(user.username)
	todo = list()
	for seat in Seat.objects.select_related('user').filter(name='hoofd'):
		todo.append(seat)
	for seat in KnGroup.objects.get(name='hoofden').seat_set.all():
		todo.append(seat)
	for seat in todo:
		seen.add(seat.user.username)
		if not seat.user.username in accounted:
			seat.user.groups.add(choofden)
			seat.user.save()
			accounted.add(seat.user.username)
			print "notice Added %s to hoofden for %s" % (
					seat.user.username, seat)
	for unacc in accounted - seen:
		KnUser.objects.get(username=unacc).groups.remove(choofden)
		print "notice Removed %s from hoofden" % unacc
