# vim: et:sta:bs=2:sw=4:
import string
import logging
import subprocess

from kn.base._random import pseudo_randstr

def pdbedit_list():
	users = dict()
	ph = subprocess.Popen(['pdbedit', '-L'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, close_fds=True)
	for line in ph.communicate()[0].splitlines():
		(username, uid, realname) = line.split(':', 2)
		users[username] = {'username': username,
                   'uid': uid,
                   'realname': realname}
	ph = subprocess.Popen(['pdbedit', '-Lw'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, close_fds=True)
	for line in output.communicate()[0].splitlines():
		(username, uid, lanmanhash, nthash, flags,
                lastchange, empty) = line.split(':')
		users[username].update({
			'lanmanhash': lanmanhash, # Unused
			'nthash': nthash,
			'lastchange': lastchange[4:],
			'flag_user': 'U' in flags,
			'flag_nullpassword': 'N' in flags, # Unused
			'flag_disabled': 'D' in flags,
			'flag_noexpire': 'X' in flags, # Unused
			'flag_workstationtrust': 'W' in flags }) # Unused
	return users

def samba_setpass(cilia, user, password):
	ph = subprocess.Popen(['smbpasswd', '-as', user],
			stdin=subprocess.PIPE, stdout=subprocess.PIPE,
			stderr=subprocess.STDOUT, close_fds=True)
	return ph.communicate("%s\n" % password)[0]

def set_samba_map(cilia, _map):
    l = logging.getLogger(__name__)
	smbusers = pdbedit_list()
	smbusers_surplus = set(smbusers)
	added_users = False
	# Determine which are missing
	for user in _map['users']:
		# This filters accents
		fn = filter(lambda x: x in string.printable,
				_map['users'][user]['full_name'])
		if user not in smbusers:
			l.info("Added %s", user)
			bogus_password = pseudo_randstr(16)
			ph = subprocess.Popen(['pdbedit', '-a', '-t',
                        '-u', user, '-f', fn],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, close_fds=True)
			ph.communicate("%s\n%s\n" % (bogus_password,
                            bogus_password))
			added_users = True
            continue
        smbusers_surplus.remove(user)
        if fn != smbusers[user]['realname']:
            subprocess.call(['pdbedit', '-u', user, '-f', fn])
            l.info("Updated %s' realname", user)
	if added_users:
		smbusers = pdbedit_list()
	for user in _map['users']:
		if (user in _map['groups']['leden']
                and smbusers[user]['flag_disabled']):
			subprocess.call(['smbpasswd', '-e', user])
			l.info("Enabled %s", user)
		if (user not in _map['groups']['leden']
                and not smbusers[user]['flag_disabled']):
			subprocess.call(['smbpasswd', '-d', user])
			l.info("Disabled %s", user)
	for user in smbusers_surplus:
		l.info("Removing stray user %s", user)
		subprocess.call(['pdbedit', '-x', '-u', user])