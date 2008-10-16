from common import *

import os
import grp
import pwd
import os.path
from kn.leden.models import Member, Commission, Seat, Alias

def sync_unix():
	gr_accounted = set()
	usr_accounted = set()
	fmap = dict()
	rmap = dict()
	for c in Commission.objects.all():
		gr_accounted.add('kn-'+c.name)
		fmap[c.name] = set()
		try:
			gmembers = grp.getgrnam("kn-"+c.name)[3]
		except KeyError:
			print "unix add-group kn-%s" % c.name
			continue
		fmap[c.name] = set(gmembers)
	for gr, gr_members in fmap.iteritems():
		for gr_member in gr_members:
			if not gr_member in rmap:
				rmap[gr_member] = set()
			rmap[gr_member].add(gr)
	pw_users = set(map(lambda x: x[0], pwd.getpwall()))
	for m in Member.objects.select_related('groups').all():
		usr_accounted.add(m.username)
		if not m.username in pw_users:
			print "unix add-user %s" % m.username
		_grp_accounted = set()
		for g in m.groups.all():
			_grp_accounted.add(g.name)
			if not m.username in fmap[g.name]:
				print "unix add-to kn-%s %s" % (g.name, m.username)
		for stray_g in  rmap[m.username] - _grp_accounted:
			print "unix rm-from kn-%s %s" % (stray_g, m.username)
	for line in grp.getgrall():
		group = line[0]
		if group[0:3] == 'kn-' and not group in gr_accounted:
			print "warn Stray group %s" % group
	for user in os.listdir(MEMBERS_HOME):
		if not user in usr_accounted:
			print "warn Stray unix user %s" % user
