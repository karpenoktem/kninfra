from common import *
import MySQLdb
import time

def execute(args):
	if len(args) < 1:
		print "Missing forum login file"
		return -4
	login = read_ssv_file(args[0])
	db = MySQLdb.connect(host='localhost', user=login[0],
			     passwd=login[2], db=login[1])
	
	if len(args) < 2:
		print "Missing action"
		return -1
	cmd = args[1]
	if cmd == 'user-add':
		if len(args) != 4:
			print "Expecting 3 arguments"
			return -2
		username = args[2]
		fn = args[3]
		c = db.cursor()
		c.execute("INSERT INTO users (`username`,"+
					     "`password`,"+
					     "`email`,"+
					     "`realname`,"+
					     "`registered`)"+
			   "VALUES (%s, %s, %s, %s, %s);",
			   (username, '37', username+'@'+MAILDOMAIN,
			    fn, int(time.time())))
	else:
		print "Unknown command"
		return -3
	
	

