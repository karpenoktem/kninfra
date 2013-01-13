# vim: et:sta:bs=2:sw=4:
import kn.leden.entities as Es
from kn import settings

def find_name_for_user(first_name, last_name):
    """ Given the first and the last name of a user, find a free name """
    names = Es.names()
    def clean(s):
        return filter(lambda x: x in settings.USERNAME_CHARS, s.lower())
    def clean_ln(s):
        if ',' in s:
            bits  = s.split(',',2)
            s = bits[1] + ' ' + bits[0]
        s = s.lower()
        s = s.replace('van ', 'v ')
        s = s.replace('de ', 'd ')
        s = s.replace('der ', 'd ')
        s = s.replace('den ', 'd ')
        return clean(s)
    fn = clean(first_name)
    ln = clean_ln(last_name)
    users = [u for u in Es.users() if u.first_name
                        and clean(u.first_name) == fn]
    # First, simply try the first_name.  This is OK if the name is not taken
    # and there is noone else with that first_name.
    if fn not in names and len(users) == 0:
        return fn
    # Try first_name with a few letters of last_name.
    for i in xrange(len(ln)):
        n = fn + ln[:i+1]
        if n in names:
            continue
        ok = True
        for u in users:
            un = clean(u.first_name) + clean_ln(u.last_name)
            if un.startswith(n):
                ok = False
                break
        if ok:
            return n
    # Try <first_name><last_name><i> for i in {2,3,...}
    i = 1
    while True:
        i += 1
        n = fn + ln + str(i)
        if n not in names:
            return n
