#!/usr/bin/env python

import subprocess

def execute(args):
	if len(args) < 1:
		print "Missing command"
		return -1
	cmd = args[0]
	if cmd == 'add-user':
		if len(args) != 2:
			print 'Expecting 2 arguments'
			return -2
		user = args[1]
		home = '/home/kn/%s' % user
		subprocess.call(['mkdir', home])
		subprocess.call(['useradd', '-d', home, '-g', 'kn', user])
		subprocess.call(['chown', '%s:kn' % user, home])
		subprocess.call(['chmod', '750', home])
	elif cmd == 'add-group':
		if len(args) != 2:
			print 'Expecting 2 arguments'
			return -3
		group = args[1]
		rawname = group.split('kn-')[1]
		home = '/groups/kn/%s' % rawname
		subprocess.call(['mkdir', home])
		subprocess.call(['groupadd', group])
		subprocess.call(['chown', 'root:%s' % group, home])
		subprocess.call(['chmod', '770', home])
	elif cmd == 'add-to':
		if len(args) != 3:
			print 'Expecting 3 arguments'
			return -4
		group = args[1]
		user = args[2]
		subprocess.call(['gpasswd', '-a', user, group])
	elif cmd == 'rm-from':
		if len(args) != 3:
			print 'Expecting 3 arguments'
			return -5
		group = args[1]
		user = args[2]
		subprocess.call(['gpasswd', '-d', user, group])
	else:
		print 'Unknown command %s'
		return -5
	
