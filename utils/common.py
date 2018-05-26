# vim: et:sta:bs=2:sw=4:

import _import  # noqa: F401
import random
import unicodedata

from django.utils import six
from django.utils.six.moves import range

import kn.settings

ALPHA = 'qwertyuiopasdfghjklzxcvbnm'
NUM = '1234567890'
ALPHANUMUL = ALPHA + ALPHA.upper() + NUM


def read_ssv_file(filename):
    """ Reads values seperated by spaces in a simple one line file """
    with open(filename) as f:
        return f.readline()[:-1].split(' ')


def sesc(t):
    return t.replace('\\', '\\\\').replace(' ', '\\ ')


def pseudo_randstr(length=12, cs=ALPHANUMUL):
    ret = ''
    for i in range(length):
        ret += cs[random.randint(0, len(cs) - 1)]
    return ret


"""
Given a list of names,
returns the users which are
  0.  named in this list,
  1.  members of groups named in this list,
  2.  members of groups of members of groups named in this list,
       ...

and raises a NotImplemtedError when another type of
Entity then "user" or "group" is encountered.

Cycles are accounted for.
"""


def args_to_users(args):
    import kn.leden.entities as Es
    ret = set()  # set of Entities found
    had = set()  # set of Entities dealt with
    todo = set()  # set of Entities to be dealt with
    todo.update(six.itervalues(Es.by_names(args)))
    while len(todo) > 0:
        e = todo.pop()
        if e in had:
            continue
        had.add(e)
        if e.type == "user":
            ret.add(e)
            continue
        if e.type != "group":
            raise NotImplementedError()
        todo.update(e.get_members())
    return tuple(ret)


def print_table(data, separator=' '):
    if len(data) == 0:
        return
    ls = [max([len(data[y][x])
               for y in range(len(data))])
          for x in range(len(data[0]))]
    for d in data:
        line = ''
        for i, b in enumerate(d):
            line += b + (' ' * (ls[i] - len(b))) + separator
        print(line)


def emailfy_name(first, last):
    first, last = map(lambda x: unicodedata.normalize(
        'NFKD', x).encode('ASCII', 'ignore'),
        (first, last))
    if ',' in last:
        bits = last.split(',', 1)
        last = bits[1] + ' ' + bits[0]
    n = first + ' ' + last
    while '  ' in n:
        n = n.replace('  ', ' ')
    n = n.replace(' ', '.').lower()
    for c in n:
        if c not in EMAIL_ALLOWED:
            raise "Invalid character %s found" % c
    return n


MAILDOMAIN = kn.settings.MAILDOMAIN
LISTDOMAIN = 'lists.' + MAILDOMAIN

EMAIL_ALLOWED = frozenset(
    [chr(ord('a') + x) for x in range(26)] +
    [chr(ord('A') + x) for x in range(26)] +
    [chr(ord('0') + x) for x in range(10)] +
    ['.', '-'])

GALLERY_PATH = '/var/galleries/kn/'
MEMBERS_HOME = '/home/kn/'
MEMBER_PHOTO_DIR = 'fotos/'
MEMBERS_ALBUM = 'per-lid'

GCAL_MAIN = 'vssp95jliss0lpr768ec9spbd8@group.calendar.google.com'
GCAL_UIT = '56ndj4j9iei03ahqa7fkrl566s@group.calendar.google.com'
GCAL_BD = '3p6k3ge8476t1bs5c20khat1uc@group.calendar.google.com'

MEMBER_GROUP = 'leden7'
DAYS_IN_YEAR = 365.242199

INST_RU = 2
INST_HAN = 1
