from kn.leden.models import Member, Commission, Seat, Alias

def sync_commissions():
	leden = Commission.objects.get(name='leden')
	accounted = set()
	for user in leden.user_set.all():
		accounted.add(user.username)
	for user in Member.objects.all():
		if not user.username in accounted:
			user.groups.add(leden)
			user.save()
			print "notice Added %s to leden" % user.username
	
	mannen = Commission.objects.get(name='mannen')
	accounted = set()
	seen = set()
	for user in mannen.user_set.all():
		accounted.add(user.username)
	for user in Member.objects.filter(gender='m'):
		seen.add(user.username)
		if not user.username in accounted:
			user.groups.add(mannen)
			user.save()
			print "notice Added %s to mannen" % user.username
	for unacc in accounted - seen:
		Member.objects.get(username=unacc).groups.remove(mannen)
		print "notice Removed %s from mannen" % unacc

	vrouwen = Commission.objects.get(name='vrouwen')
	accounted = set()
	seen = set()
	for user in vrouwen.user_set.all():
		accounted.add(user.username)
	for user in Member.objects.filter(gender='v'):
		seen.add(user.username)
		if not user.username in accounted:
			user.groups.add(vrouwen)
			user.save()
			print "notice Added %s to vrouwen" % user.username
	for unacc in accounted - seen:
		Member.objects.get(username=unacc).groups.remove(vrouwen)
		print "notice Removed %s from vrouwen" % unacc
	
	choofden = Commission.objects.get(name='hoofden')
	accounted = set()
	seen = set()
	for user in choofden.user_set.all():
		accounted.add(user.username)
	for seat in Seat.objects.select_related('member').filter(name='hoofd'):
		seen.add(seat.member.username)
		if not seat.member.username in accounted:
			seat.member.groups.add(choofden)
			seat.member.save()
			accounted.add(seat.member.username)
			print "notice Added %s to hoofden for %s" % (
					seat.member.username, seat)
	for unacc in accounted - seen:
		Member.objects.get(username=unacc).groups.remove(choofden)
		print "notice Removed %s from hoofden" % unacc
