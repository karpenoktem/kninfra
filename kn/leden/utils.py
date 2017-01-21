import kn.leden.entities as Es

from django.conf import settings
from django.utils import dateparse

import unidecode
import datetime


def find_name_for_user(first_name, last_name):
    """ Given the first and the last name of a user, find a free name """
    def clean(s, last_name=False, capitalize_tussenvoegsels=False):
        """ Cleans a first or last name.  We do some extra things for last
            names and optionally capitalize letters that came
            from tussenvoegsels. """
        if last_name and ',' in s:
            bits = s.split(',', 2)
            s = bits[1] + ' ' + bits[0]
        s = unidecode.unidecode(s).lower()
        s = filter(lambda x: x in settings.USERNAME_CHARS + ' ', s)
        if last_name:
            s = s.replace('van ', 'V ')
            s = s.replace('der ', 'D ')
            s = s.replace('de ', 'D ')
            s = s.replace('den ', 'D ')
            if not capitalize_tussenvoegsels:
                s = s.lower()
        return s.replace(' ', '')

    names = Es.names()
    fn = clean(first_name)
    ln_ctv = clean(last_name, last_name=True, capitalize_tussenvoegsels=True)
    ln = clean(last_name, last_name=True)
    # Others users with this firstname
    users_with_same_fn = [u for u in Es.users() if u.first_name
                                and clean(u.first_name) == fn]
    # Try first_name or first_name with a few letters of the last_name appended
    for i in xrange(len(ln)+1):
        n = fn + ln[:i]
        # Don't try giedov, but directly giedovdm if the name is derived
        # from `Giedo van der Meer'.
        if i and ln_ctv[:i][-1].isupper():
            continue
        if n in names:
            continue
        # Recall `Giedo Jansen' has the username `giedo'.  Suppose there is
        # a new member called `Giedo Joosten'. In this case we want to give
        # him the username `giedojo' instead of `giedoj'.
        ok = True
        for u in users_with_same_fn:
            un = clean(u.first_name) + clean(u.last_name, last_name=True)
            if un.startswith(n):
                ok = False
                break
        if ok:
            return n
    # Last resort: try <first_name><last_name><i> for i in {2,3,...}
    i = 1
    while True:
        i += 1
        n = fn + ln + str(i)
        if n not in names:
            return n


def parse_date(s):
    '''
    Converts a string in the form YYYY-MM-DD to a datetime object.
    '''
    date = dateparse.parse_date(s)
    if date is None:
        return None
    return datetime.datetime(date.year, date.month, date.day, 0, 0)

# vim: et:sta:bs=2:sw=4:
