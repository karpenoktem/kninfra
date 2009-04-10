from common import *

import MySQLdb
from kn.leden.models import KnUser, KnGroup, Seat, Alias
import Mailman
import Mailman.Utils

def emailfy_name(first, last):
	if ',' in last:
		bits = last.split(',', 1)
		last = bits[1] + ' ' + bits[0]
	n = first + ' ' + last
	while '  ' in n:
		n = n.replace('  ', ' ')
	n = n.replace(' ', '.').lower()
	for c in n:
		if not c in EMAIL_ALLOWED:
			raise "Invalid character %s found" % c
	return n

def sync_vpopmail():
	login = read_ssv_file('vpopmail.login')
	db = MySQLdb.connect(host='localhost', user=login[0],
		passwd=login[2], db=login[1])
	c = db.cursor()
	c.execute("SELECT alias, valias_line FROM valias WHERE domain=%s",
		(MAILDOMAIN, ))
	map = dict()
	claimed = set()
	for alias, target in c.fetchall():
		assert target[0] == '&'
		target = target[1:]
		map[alias] = target

	for user in KnUser.objects.all():
		claimed.add(user.username)
		if not user.username in map:
			print "vpopmail add %s %s" % (user.username, user.email)
		elif map[user.username] != user.email:
			print "vpopmail alter %s %s # was %s" % (
				user.username, user.email, map[user.username])
		fn = emailfy_name(user.first_name, user.last_name)
		claimed.add(fn)
		if not fn in map:
			print "vpopmail add %s %s" % (fn, user.primary_email)
		elif map[fn] != user.primary_email:
			print "vpopmail alter %s %s # was %s" % (
				fn, user.primary_email, map[fn])

	for list in Mailman.Utils.list_names():
		if list in claimed:
			print "warn CONFLICT %s already claimed (Mailman)" % list
			continue
		claimed.add(list)
		if not list in map:
			print "vpopmail add %s %s@%s" % (list, list, LISTDOMAIN)
			continue
		if map[list] != "%s@%s" % (list, LISTDOMAIN):
			print "vpopmail alter %s %s@%s # was %s" % (
					list, list, LISTDOMAIN, map[list])

	for seat in Seat.objects.select_related('group', 'user').all():
		name, email = seat.primary_name, seat.primary_email
		temail = seat.user.primary_email		
		if name in claimed:
			print "warn CONFLICT %s already claimed (Seat)" % email
			continue
		claimed.add(name)
		if not name in map:
			print "vpopmail add %s %s" % (name, temail)
			continue
		if map[name] != temail:
			print "vpopmail alter %s %s # was %s" % (
					name, temail, map[name])

	for alias in Alias.objects.all():
		if alias.source in claimed:
			print "warn CONFLICT %s already claimed (Alias)" % alias.source
			continue
		claimed.add(alias.source)
		if not alias.source in map:
			print "vpopmail add %s %s@%s" % (alias.source, alias.target, MAILDOMAIN)
			continue
		if map[alias.source] != "%s@%s" % (alias.target, MAILDOMAIN):
			print "vpopmail alter %s %s@%s # was %s" % (
					alias.source, alias.target, MAILDOMAIN, map[alias.source])

	for alias, target in map.iteritems():
		if not alias in claimed:
			print "warn STRAY %s -> %s" % (alias, target)

