import pwd
import grp
import crypt
import string
import logging
import subprocess

from kn.base._random import pseudo_randstr

def unix_setpass(cilia, user, password):
        crypthash = crypt.crypt(password, pseudo_randstr(2))
        subprocess.call(['usermod', '-p', crypthash, user])

def set_unix_map(cilia, _map):
        # First get the list of all current users
        kn_gid = grp.getgrnam('kn').gr_gid
        c_users = set([u.pw_name for u in pwd.getpwall() if u.pw_gid == kn_gid])
        # Determine which are missing
        for user in _map['users']:
                if user not in c_users:
                        home = '/home/%s' % user
                        fn = filter(lambda x: x in string.printable,
                                        _map['users'][user])
                        subprocess.call(['mkdir', home])
                        subprocess.call(['useradd', '-d', home, '-g', 'kn',
                                '-c', fn, user])
                        subprocess.call(['chown', '%s:kn' % user, home])
                        subprocess.call(['chmod', '750', home])
        # Get list of all groups
        gs = grp.getgrall()
        c_groups = set([g.gr_name for g in gs
                        if g.gr_name.startswith('kn-')])
        # Determine which are missing
        for g in _map['groups']:
                gname = ('kn-%s'%g)[:32]
                if gname not in c_groups:
                        home = '/groups/%s'%g
                        subprocess.call(['mkdir', home])
                        subprocess.call(['groupadd', gname])
                        subprocess.call(['chown', 'root:%s'%gname, home])
                        subprocess.call(['chmod', '770', home])
        # Synchronise membership
        glut = dict()
        for g in gs:
                assert g.gr_name not in glut # issue #5
                glut[g.gr_name] = g
        for g in _map['groups']: 
                gname = ('kn-'+g)[:32]
                c_memb = set(glut[gname].gr_mem)
                w_memb = set(_map['groups'][g])
                for m in w_memb:
                        if m in c_memb:
                                continue
                        subprocess.call(['gpasswd', '-a', m, gname])
                for m in c_memb:
                        if m in w_memb:
                                continue
                        subprocess.call(['gpasswd', '-d', m, gname])
