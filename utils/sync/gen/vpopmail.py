from common import *

import MySQLdb
from kn.leden.models import OldKnUser, KnGroup, Seat, Alias
import Mailman
import Mailman.Utils

def get_current_map():
	login = read_ssv_file('vpopmail.login')
	db = MySQLdb.connect(host='localhost', user=login[0],
		passwd=login[2], db=login[1])
	c = db.cursor()
	c.execute("SELECT alias, valias_line FROM valias WHERE domain=%s",
		(MAILDOMAIN, ))
	_map = dict()
	for alias, target in c.fetchall():
		assert target[0] == '&'
		target = target[1:]
		if not alias in _map:
			_map[alias] = set()
		_map[alias].add(target)
	return _map

def get_desired_map():
	_map = dict()
	def claim(name, email, reason):
		if not name in _map:
			_map[name] = set()
		_map[name].add((email, reason))
	for user in OldKnUser.objects.all():
		claim(user.username, user.email, 'user.name')
		fn = emailfy_name(user.first_name, user.last_name)
		claim(fn, user.primary_email, 'user.fullname')
	for list in Mailman.Utils.list_names():
		claim(list, list + '@' + LISTDOMAIN, 'mailinglist')
	for seat in Seat.objects.select_related('group', 'user').all():
		name, email = seat.primary_name, seat.primary_email
		temail = seat.user.primary_email		
		claim(name, temail, 'seat')
	for alias in Alias.objects.all():
		claim(alias.source, alias.target + '@' + MAILDOMAIN, 'alias')
	return _map

def check_desired_map(dmap):
	for name, targets in dmap.iteritems():
		if len(set(map(lambda x: x[1], targets))) != 1:
			print "# vpopmail, multiclaim with distinct reasons:"
			print "# %s ->" % name
			for target, reason in targets:
				print "#    %s (%s)" % (target, reason)

def sync_vpopmail():
	cmap = get_current_map()
	dmap = get_desired_map()
	check_desired_map(dmap)
	clut = set()
	dlut = set()
	for name, targets in cmap.iteritems():
		for target in targets:
			clut.add("%s\0%s" % (name, target))
	for name, targets in dmap.iteritems():
		for target, reason in targets:
			dlut.add("%s\0%s" % (name, target))
			if not "%s\0%s" % (name, target) in clut:
				print "vpopmail add %s %s # %s" % (
						name, target, reason)
	for name, targets in cmap.iteritems():
		for target in targets:
			if not "%s\0%s" % (name, target) in dlut:
				print "# vpopmail STRAY %s -> %s" % (
						name, target)
