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
	elif cmd == "gal-rm":
		if len(args)!=2:
			print "Not exactly one argument given."
			return -1
		pth = os.path.join(GALLERY_PATH, MEMBERS_ALBUM, args[1])
		os.unlink(pth)
	elif cmd == "adm-add":
		if len(args)!=5:
			print "Not exactly 4 arguments given."
			return -1
		c = getDbCursor()
		c.execute("INSERT INTO zp_administrators (user,name,email,"+
				"rights,password) VALUES (%s,%s,%s,%s,%s)",
				(args[1],args[2],args[3],args[4],"37"))
		c.close()
	elif cmd == "adm-update":
		if len(args)!=4:
			print "Not exactly 3 arguments given."
			return -1
		c = getDbCursor()
		assert(args[2] in ['name'])
		q = "UPDATE zp_administrators SET %s=%%s WHERE user=%%s"%args[2]
		c.execute(q,(args[3],args[1]))
		c.close()
	elif cmd == "adm2alb-add":
		if len(args)!=3:
			print "Not exactly 3 arguments given."
			return -1
		c = getDbCursor()
		user = args[1]
		folder = args[2]
		
		c.execute("SELECT id FROM zp_administrators WHERE user=%s",user)
		admid, = c.fetchone()
		c.execute("SELECT id FROM zp_albums WHERE folder=%s", folder)
		albid, = c.fetchone()
		
		c.execute("""INSERT INTO zp_admintoalbum (albumid,adminid) 
				VALUES (%s,%s)""", (albid,admid))
		
		c.close()
	else:
		print "Unknown command: %s" % cmd
		return -1
	
def getDbCursor():
	user, db, passwd = read_ssv_file('photos.login')
	dc = MySQLdb.connect(host='localhost', user=user, db=db, 
				passwd=passwd)
	return dc.cursor()
