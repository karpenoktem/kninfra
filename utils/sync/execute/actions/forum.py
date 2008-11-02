from common import *
import MySQLdb
import time

def execute(args):
	login = read_ssv_file('forum.login')
	db = MySQLdb.connect(host='localhost', user=login[0],
			     passwd=login[2], db=login[1])
	
	if len(args) < 1:
		print "Missing action"
		return -1
	cmd = args[0]
	if cmd == 'user-add':
		if len(args) != 3:
			print "Expecting 3 arguments"
			return -2
		username = args[1]
		fn = args[2]
		c = db.cursor()
		c.execute("INSERT INTO users (`username`,"+
					     "`password`,"+
					     "`email`,"+
					     "`realname`,"+
					     "`registered`)"+
			   "VALUES (%s, %s, %s, %s, %s);",
			   (username, '37', username+'@'+DOMAIN,
			    fn, int(time.time())))
	else:
		print "Unknown command"
		return -3
	
	

