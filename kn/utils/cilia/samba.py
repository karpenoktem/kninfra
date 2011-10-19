import subprocess
import datetime

from string import join

def samba_setpass(cilia, user, password):
	pass # TODO

def set_samba_map(cilia, _map):
	config = list()
	config.append("# Automatically generated by Cilia.set_samba_map()")
	for g in _map['groups']:
		gname = ('kn-%s'%g)[:32]
		config.append("[%s]" % g)
		config.append("comment = %s" % g)
		config.append("path = /groups/%s" % g)
		config.append("valid users = %s" % join(_map['groups'][g], ' '))
		config.append("")
	group_config = join(config, "\n")
	print group_config
	with open("/etc/samba/groups.conf", "w") as gc:
		gc.write(group_config)
	with open("/etc/samba/base.conf") as bc:
		base = bc.read()
	with open("/etc/samba/smb.conf", "w") as fc:
		fc.write(base)
		fc.write(group_config)
	# We could SIGHUP samba but it picks up new configurations each minute anyway
