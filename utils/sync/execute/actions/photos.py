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
	if cmd == 'mkdir':
		if len(args)!=2:
			print "Not exactly one argument given."
			return -1
		os.mkdir(args[1])
	elif cmd == "symlink":
		if len(args)!=3:
			print "Not exactly two arguments given."
			return -1
		os.symlink(args[1],args[2])
	elif cmd == "rm":
		if len(args)!=2:
			print "Not exactly one argument given."
			return -1
		os.unlink(args[1])
	elif cmd == "adm-add":
		c = getDbCursor()
		c.execute("INSERT INTO zp_administrators (user,name,email,"+
				"rights,password) VALUES (%s,%s,%s,%s,%s)",
				(args[1],args[2],args[3],args[4],"37"))
	elif cmd == "adm-update":
		c = getDbCursor()
		assert(args[2] in ['name'])
		q = "UPDATE zp_administrators SET %s=%%s WHERE user=%%s"%args[2]
		c.execute(q,(args[3],args[1]))
	else:
		print "Unknown command: %s" % cmd
		return -1
	
def getDbCursor():
	user, db, passwd = read_ssv_file('photos.login')
	dc = MySQLdb.connect(host='localhost', user=user, db=db, 
				passwd=passwd)
	return dc.cursor()
