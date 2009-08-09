import _import

import sys
from common import *
from kn.leden.models import OldKnUser, KnGroup

users = dict()
if len(sys.argv) == 1:
	_users = OldKnUser.objects.all()
else:
	_users = args_to_users(sys.argv[1:])

for m in _users:
	users[m.username] = set()

i = 0
while True:
	i += 1
	try:
		g = KnGroup.objects.get(name='leden%s'%i)
	except KnGroup.DoesNotExist:
		break
	for m in g.user_set.all():
		if m.username in users:
			users[m.username].add(i)
nyears = i - 1

for m, ys in users.iteritems():
	print "%15s" % m,
	for y in xrange(1, nyears + 1):
		print '*' if y in ys else ' ',
	print

