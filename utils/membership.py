import _import

from kn.leden.models import KnUser, KnGroup

users = dict()
for m in KnUser.objects.all():
	users[m.username] = set()

i = 0
while True:
	i += 1
	try:
		g = KnGroup.objects.get(name='leden%s'%i)
	except KnGroup.DoesNotExist:
		break
	for m in g.user_set.all():
		users[m.username].add(i)
nyears = i - 1

for m, ys in users.iteritems():
	print "%15s" % m,
	for y in xrange(1, nyears + 1):
		print '*' if y in ys else ' ',
	print

