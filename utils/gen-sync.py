from __future__ import with_statement
import _import

import grp
import pwd
import sys
import MySQLdb
import os.path
from common import *
import Mailman
import Mailman.Utils
import Mailman.MailList
from kn.leden.models import Member, Commission, Seat, Alias

DOMAIN = 'karpenoktem.nl'
LISTDOMAIN = 'lists.karpenoktem.nl'


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


def sync_mailman():
	mls = set(Mailman.Utils.list_names())
	coms = set()
	for com in Commission.objects.all():
		coms.add(com.name)
		if not com.name in mls:
			print "mailman create %s" % com
			continue
		m = Mailman.MailList.MailList(com.name, lock=False)
		accounted = set()
		for user in com.user_set.all():
			email = "%s@%s" % (user, DOMAIN)
			accounted.add(email)
			if not email in m.members:
				print "mailman subscribe %s %s" % (com.name, email)
		for member, dummy in m.members.iteritems():
			if not member in accounted:
				print "mailman unsubscribe %s %s" % (com.name, member)
	for ml in mls:
		if not ml in coms:
			print "warn STRAY mailinglist %s" % ml 

def sync_unix():
	gr_accounted = set()
	usr_accounted = set()
	map = dict()
	for c in Commission.objects.all():
		gr_accounted.add('kn-'+c.name)
		map[c.name] = set()
		try:
			gmembers = grp.getgrnam("kn-"+c.name)[3]
		except KeyError:
			print "unix add-group kn-%s" % c.name
			continue
		map[c.name] = set(gmembers)
	for m in Member.objects.select_related('groups').all():
		usr_accounted.add(m.username)
		try:
			pwd.getpwnam(m.username)
		except KeyError:
			print "unix add-user %s" % m.username
		for g in m.groups.all():
			if not m.username in map[g.name]:
				print "unix add-to kn-%s %s" % (g.name, m.username)
	for line in grp.getgrall():
		group = line[0]
		if group[0:3] == 'kn-' and not group in gr_accounted:
			print "warn Stray group %s" % group
	for user in os.listdir('/home/kn'):
		if not user in usr_accounted:
			print "warn Stray unix user %s" % user


EMAIL_ALLOWED = frozenset(
		    map(lambda x: chr(ord('a') + x), xrange(26)) +
		    map(lambda x: chr(ord('A') + x), xrange(26)) +
		    map(lambda x: chr(ord('0') + x), xrange(10)) +
		    ['.', '-'])
	
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
		(DOMAIN, ))
	map = dict()
	claimed = set()
	for alias, target in c.fetchall():
		assert target[0] == '&'
		target = target[1:]
		map[alias] = target

	for user in Member.objects.all():
		claimed.add(user.username)
		if not user.username in map:
			print "vpopmail add %s %s" % (user.username, user.email)
		elif map[user.username] != user.email:
			print "vpopmail alter %s %s # was %s" % (
				user.username, user.email, map[user.username])
		fn = emailfy_name(user.first_name, user.last_name)
		claimed.add(fn)
		if not fn in map:
			print "vpopmail add %s %s" % (fn, user.username+"@"+DOMAIN)
		elif map[fn] != user.username+"@"+DOMAIN:
			print "vpopmail alter %s %s@%s # was %s" % (
				fn, user.username, DOMAIN, map[fn])

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

	for seat in Seat.objects.select_related('commission', 'member').all():
		if seat.isGlobal:
			name, email = seat.name, "%s@%s" % (seat.name, DOMAIN)
		else:
			name, email = seat.commission.name + '-' + seat.name, \
				"%s-%s@%s" % (seat.commission.name, seat.name, DOMAIN)
		temail = seat.member.username + '@' + DOMAIN		
		if seat.name in claimed:
			print "warn CONFLICT %s already claimed (Seat)" % email
			continue
		claimed.add(name)
		if not name in map:
			print "vpopmail add %s %s@%s" % (name, seat.member.username, DOMAIN)
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
			print "vpopmail add %s %s@%s" % (alias.source, alias.target, DOMAIN)
			continue
		if map[alias.source] != "%s@%s" % (alias.target, DOMAIN):
			print "vpopmail alter %s %s@%s # was %s" % (
					alias.source, alias.target, DOMAIN, map[alias.source])

	for alias, target in map.iteritems():
		if not alias in claimed:
			print "warn STRAY %s -> %s" % (alias, target)

def sync_all():
	sync_commissions()
	sync_vpopmail()
	sync_mailman()
	sync_unix()

if __name__ == '__main__':
	p = os.path.dirname(sys.argv[0])
	if p != '': os.chdir(p)
	sync_all()
