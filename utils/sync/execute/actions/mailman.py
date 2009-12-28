#!/usr/bin/env python

import _import

import sys
from subprocess import call, Popen, PIPE
from os import path
from Mailman import Utils, MailList, UserDesc

def execute(args):
	if len(args) < 1:
		print 'Missing command'
		return -1
	cmd = args[0]
	if cmd == 'subscribe':
		if len(args) != 3:
			print 'Expected 3 parameters'
			return -2
		m = MailList.MailList(args[1])
		try:
			pw = Utils.MakeRandomPassword()
			desc = UserDesc.UserDesc(args[2], '', pw, False)
			m.ApprovedAddMember(desc, False, False)
			m.Save()
		finally:
			m.Unlock()
	elif cmd == 'unsubscribe':
		if len(args) != 3:
			print 'Expected 3 parameters'
			return -3
		m = MailList.MailList(args[1])
		try:
			m.ApprovedDeleteMember(args[2], admin_notif=False,
					userack=False)
			m.Save()
		finally:
			m.Unlock()
	elif cmd == "create":
		if len(args) != 2:
			print "Expected 1 parameter"
			return -4
		list_name = args[1]
		
		# First, create an unpopulated unconfigured mailing list
		#  using one of the mailman scripts.
		#
		# $ ~mailman/bin/newlist --help
		# Usage: ./newlist [options] [listname [listadmin-addr 
		#					[admin-password]]]
		#  [...]
		#
		# Note that newlist will wait for a newline.
		expath = path.expanduser("~mailman/bin/newlist")
		pwd = Popen("/root/bin/passgen", stdout=PIPE
				).communicate()[0].strip()
		cmd = [expath, list_name, "wortel@karpenoktem.nl", pwd]
		Popen(cmd, stdin=PIPE, stdout=PIPE).communicate()
		
		raise NotImplementedError()

		call(["cp", "--recursive", "--no-target-directory",
			"--force",
			"/var/lib/mailman/lists/skel",
			"/var/lib/mailman/lists/%s" % list_name])
	else:
		print 'Unknown command'
		return -5
