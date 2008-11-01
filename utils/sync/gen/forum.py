from common import *

import MySQLdb
from kn.leden.models import Member, Commission, Seat, Alias

def sync_forum():
	login = read_ssv_file('forum.login')
	db = MySQLdb.connect(host='localhost', user=login[0],
		passwd=login[2], db=login[1])
	c = db.cursor()
	c.execute("SELECT `username` FROM users;")
	forum_users = set()
	for username, in c.fetchall():
		forum_users.add(username)
	forum_users_unaccounted = set(forum_users)
	for m in Member.objects.all():
		if not m.username in forum_users:
			print "forum user-add %s %s" % (m.username,
						   sesc(m.get_full_name()))
			continue
		forum_users_unaccounted.remove(m.username)
	for m in forum_users_unaccounted:
		print "warn forum: unaccounted user %s" % m
