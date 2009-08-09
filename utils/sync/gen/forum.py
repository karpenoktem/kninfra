from common import *

import MySQLdb
from kn.leden.models import OldKnUser, OldKnGroup, Seat, Alias

def sync_forum(loginFile):
	login = read_ssv_file(loginFile)
	db = MySQLdb.connect(host='localhost', user=login[0],
		passwd=login[2], db=login[1])
	c = db.cursor()
	c.execute("SELECT `username` FROM users;")
	forum_users = set()
	for username, in c.fetchall():
		forum_users.add(username)
	forum_users_unaccounted = set(forum_users)
	for m in OldKnUser.objects.all():
		if not m.username in forum_users:
			print "forum %s user-add %s %s" % (
						loginFile,
						m.username,
						sesc(m.get_full_name()))
			continue
		forum_users_unaccounted.remove(m.username)
	for m in forum_users_unaccounted:
		print "warn %s: unaccounted user %s" % (loginFile, m)
