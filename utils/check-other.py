# checks for inconsistencies

import _import
from common import *
from datetime import datetime, date
from Mailman.MailList import MailList

from kn.leden.models import KnUser, KnGroup, Seat, Alias

def check_geinteresseerden():
	print "GEINTERESSEERDEN"
	es = frozenset(map(lambda m: m.email.lower(),
		KnGroup.objects.get(name=MEMBER_GROUP).user_set.all()))
	ml = MailList('geinteresseerden', False)
	for m in ml.members:
		if m.lower() in es:
			print "%s in geinteresseerden" % m

def check_namespace():
	print "NAMESPACE"
	cn = set(map(lambda c: c.name, 
		filter(lambda c: not c.isVirtual, KnGroup.objects.all())))
	un = set(map(lambda m: m.username, KnUser.objects.all()))
	sn = set(map(lambda s: s.name if s.isGlobal else s.group.name \
					+ '-' + s.name, Seat.objects.all()))
	an = set(map(lambda a: a.source, Alias.objects.all()))
	
	n = set()
	for o in (cn, un, sn, an):
		inter = n.intersection(o)
		if len(inter) != 0:
			for el in inter:
				print '%s: namespace conflict' % el
		n = n.union(o)
	
	for a in Alias.objects.all():
		if not a.target in n:
			print '%s -> %s, target doesn\'t exist' % \
					(a.source, a.target)


def check_commissions():
	print "COMMISSIONS"
	for c in KnGroup.objects.all():
		if len(c.description) < 15:
			print "%s: description too short (<15)" % c.name
		if c.isVirtual:
			if c.user_set.count() != 0:
				print "%s: virtual commission got members" % \
						c.name
if __name__ == '__main__':
	check_commissions()
	check_namespace()
	check_geinteresseerden()
