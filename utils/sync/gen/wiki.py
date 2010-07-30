from common import * #settings
import MySQLdb

from kn.leden.models import OldKnUser
import os

def sync_wiki():
	members = dict([(m.username,m) for m in OldKnUser.objects.all()])
	users = set()

	dbuser, dbname, dbpasswd = read_ssv_file('wiki.login')
	dc = MySQLdb.connect(host="localhost", user=dbuser, passwd=dbpasswd,
			db=dbname)
	c = dc.cursor()
	c.execute("""SELECT user_name FROM user""")

	for user, in c.fetchall():
		users.add(user)
		if user.lower() not in members:
			print "warn wiki user %s is not a member." % user
	
	for name, member in members.iteritems():
		if name.capitalize() in users:
			continue
		print "wiki user-add %s %s" % (name, 
				sesc(member.full_name()))
	c.close()
	dc.close()

