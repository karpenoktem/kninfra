#!/usr/bin/env python
from __future__ import with_statement

import os
import sys
import MySQLdb

DOMAIN = 'karpenoktem.nl'

def read_ssv_file(filename):
	""" Reads values seperated by spaces in a simple one line file """
	with open(filename) as f:
		return f.readline()[:-1].split(' ')

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
			  "VALUES (%s, %s, %s)", (source, '&'+target, DOMAIN))
	elif cmd == 'alter':
		if len(args) != 3:
			print "Expecting 3 arguments"
			return -3
		source = args[1]
		target = args[2]
		c = db.cursor()
		c.execute("UPDATE valias SET `valias_line`=%s "+
			  "WHERE `domain`=%s and `alias`=%s", ('&'+target, DOMAIN, source))
	else:
		print "Unknown command"
		return -4
	
	

