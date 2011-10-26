import subprocess
import datetime
import string
import logging

import cStringIO as StringIO

from kn.base._random import pseudo_randstr

def pdbedit_list():
	users = dict()

	ph = subprocess.Popen(['pdbedit', '-L'],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT, close_fds=True)
	(output, bogus) = ph.communicate()
	for line in output.splitlines():
		(username, uid, realname) = line.split(':', 2)
		users[username] = {'username': username, 'uid': uid, 'realname': realname}

	ph = subprocess.Popen(['pdbedit', '-Lw'],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT, close_fds=True)
	(output, bogus) = ph.communicate()
	for line in output.splitlines():
		(username, uid, lanmanhash, nthash, flags, lastchange, empty) = line.split(':')
		users[username].update({
			'lanmanhash': lanmanhash, # Unused
			'nthash': nthash,
			'lastchange': lastchange[4:],
			'flag_user': 'U' in flags,
			'flag_nullpassword': 'N' in flags, # Unused
			'flag_disabled': 'D' in flags,
			'flag_noexpire': 'X' in flags, # Unused
			'flag_workstationtrust': 'W' in flags, # Unused
		})

	return users

def samba_setpass(cilia, user, password):
	ph = subprocess.Popen(['smbpasswd', '-as', user],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT, close_fds=True)
	(output, bogus) = ph.communicate("%s\n" % password)
	return output

def set_samba_map(cilia, _map):
	smbusers = pdbedit_list()
	smbusers_surplus = set(smbusers)
	added_users = False
	# Determine which are missing
	for user in _map['users']:
		# This filters accents
		fn = filter(lambda x: x in string.printable,
				_map['users'][user]['full_name'])
		if user not in smbusers:
			logging.info("samba: Added %s", user)
			bogus_password = pseudo_randstr(16)
			ph = subprocess.Popen(['pdbedit', '-a', '-t',
					'-u', user, '-f', fn],
					stdin=subprocess.PIPE, stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT, close_fds=True)
			(output, bogus) = ph.communicate("%s\n%s\n" % (bogus_password, bogus_password))
			added_users = True
		else:
			smbusers_surplus.remove(user)
			if fn != smbusers[user]['realname']:
				subprocess.call(['pdbedit', '-u', user, '-f', fn])
				logging.info("samba: Updated %s' realname", user)

	if added_users:
		smbusers = pdbedit_list()

	for user in _map['users']:
		if user in _map['groups']['leden'] and smbusers[user]['flag_disabled']:
			subprocess.call(['smbpasswd', '-e', user])
			logging.info("samba: Enabled %s", user)
		if user not in _map['groups']['leden'] and not smbusers[user]['flag_disabled']:
			subprocess.call(['smbpasswd', '-d', user])
			logging.info("samba: Disabled %s", user)

	for user in smbusers_surplus:
		logging.info("samba: Removing stray user %s", user)
		subprocess.call(['pdbedit', '-x', '-u', user])
