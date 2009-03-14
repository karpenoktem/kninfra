#!/usr/bin/env python
from __future__ import with_statement
from common import *

import os
import MySQLdb

def execute(args):
	if len(args) < 1:
		print "Missing action"
		return -1
	cmd = args[0]
	if cmd == 'user-add':
		if len(args)!=3:
			print "Not exactly two argument given"
			return -1
		user, db, passwd = read_ssv_file('wiki.login')
		dc = MySQLdb.connect(host='localhost', user=user, db=db, 
					passwd=passwd)
		c = dc.cursor()
		q = ""

		with open('wiki.insert_user.sql') as f:
			q = f.read()
		
		c.execute(q, args[1], args[2], args[1]+'@'+DOMAIN)
		c.execute('commit;')
		c.close()
		dc.close()
	else:
		print "Unknown command: %s" % cmd
		return -1
