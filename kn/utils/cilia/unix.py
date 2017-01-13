import pwd
import grp
import spwd
import string
import logging
import datetime
import subprocess

def unix_setpass(cilia, user, password):
    kn_gid = grp.getgrnam('kn').gr_gid
    pwent = pwd.getpwnam(user)
    if pwent.pw_gid != kn_gid:
        return {'error': "Permission denied. Gid is not kn"}
    ph = subprocess.Popen(['chpasswd'], stdin=subprocess.PIPE)
    ph.communicate("%s:%s\n" % (user, password))
    if ph.returncode == 0:
        return {'success': True}
    return {'success': False}

def set_unix_map(cilia, _map):
    # First get the list of all current users
    kn_gid = grp.getgrnam('kn').gr_gid
    c_users = set([u.pw_name for u in pwd.getpwall() if u.pw_gid == kn_gid])
    c_users_surplus = set(c_users)
    # Determine which are missing
    for user in _map['users']:
        # This filters accents
        fn = filter(lambda x: x in string.printable,
                _map['users'][user]['full_name'])
        expire_date = _map['users'][user]['expire_date']
        if user not in c_users:
            home = '/home/%s' % user
            subprocess.call(['mkdir', home])
            subprocess.call(['useradd', '-d', home, '-g', 'kn',
                '-c', fn, '-e', expire_date, user])
            subprocess.call(['chown', '%s:kn' % user, home])
            subprocess.call(['chmod', '750', home])
        else:
            c_users_surplus.remove(user)
            pwent = pwd.getpwnam(user)
            if fn != pwent.pw_gecos:
                subprocess.call(['usermod', '-c', fn, user])
            # The +1 is due to our timezone being GMT +01:00, so
            # the unix Epoch starts at 01:00 instead of 00:00.
            # This will give an off-by-one in the date, so let's
            # correct it.
            expday = int(datetime.datetime.strptime(expire_date,
                    '%Y-%m-%d').strftime('%s')) / 86400 + 1
            spwent = spwd.getspnam(user)
            if expday != spwent.sp_expire:
                subprocess.call(['usermod', '-e',
                        expire_date, user])
    for user in c_users_surplus:
        logging.info("Removing stray user %s", user)
        subprocess.call(['userdel', '-r', user])
    # Get list of all groups
    gs = grp.getgrall()
    c_groups = set([g.gr_name for g in gs
            if g.gr_name.startswith('kn-')])
    # Determine which are missing
    created_group = False
    for g in _map['groups']:
        gname = ('kn-%s'%g)[:128]
        if gname not in c_groups:
            home = '/groups/%s'%g
            subprocess.call(['mkdir', home])
            subprocess.call(['groupadd', gname])
            subprocess.call(['chown', 'root:%s'%gname, home])
            subprocess.call(['chmod', '770', home])
            created_group = True
    if created_group:
        gs = grp.getgrall()
    # Synchronise membership
    glut = dict()
    for g in gs:
        glut[g.gr_name] = g
    for g in _map['groups']:
        gname = ('kn-'+g)[:128]
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

# vim: et:sta:bs=2:sw=4:
