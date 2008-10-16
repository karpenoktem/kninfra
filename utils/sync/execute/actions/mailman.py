#!/usr/bin/env python

import _import

import sys
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
	else:
		print 'Unknown command'
		return -4
