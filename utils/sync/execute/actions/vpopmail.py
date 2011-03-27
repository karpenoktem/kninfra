#!/usr/bin/env python
from __future__ import with_statement

import os
import sys
import MySQLdb

from common import *

def execute(args):
	login = read_ssv_file('vpopmail.login')
	db = MySQLdb.connect(host='localhost', user=login[0],
			     passwd=login[2], db=login[1])
	
	if len(args) < 1:
		print "Missing action"
		return -1
	cmd = args[0]
	if cmd == 'add':
		if len(args) != 3:
			print "Expecting 3 arguments"
			return -2
		source = args[1]
		target = args[2]
		c = db.cursor()
		c.execute("INSERT INTO valias(`alias`, `valias_line`, `domain`) "+
			  "VALUES (%s, %s, %s)", (source, '&'+target, MAILDOMAIN))
	elif cmd == 'rm':
		if len(args) != 3:
			print "Expecting 3 arguments"
			return -2
		source = args[1]
		target = args[2]
		c = db.cursor()
		c.execute("DELETE FROM valias WHERE `alias` = %s AND `valias_line` = %s AND `domain` = %s", (source, '&'+target, MAILDOMAIN))
	else:
		print "Unknown command"
		return -4
	
	

