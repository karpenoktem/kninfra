from kn.leden.models import KnUser, KnGroup, Seat, Alias

def sync_commissions():
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
	for seat in Seat.objects.select_related('user').filter(name='hoofd'):
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
