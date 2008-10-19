#!/usr/bin/env python
from __future__ import with_statement

import os

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
	else:
		print "Unknown command: %s" % cmd
		return -1
	
	

