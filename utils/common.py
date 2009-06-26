from __future__ import with_statement

import _import
import random
import kn.leden.settings

ALPHA = 'qwertyuiopasdfghjklzxcvbnm'
NUM = '1234567890'
ALPHANUMUL = ALPHA + ALPHA.upper() + NUM

def read_ssv_file(filename):
        """ Reads values seperated by spaces in a simple one line file """
        with open(filename) as f:
                return f.readline()[:-1].split(' ')

def sesc(t):
	return t.replace('\\','\\\\').replace(' ','\\ ')

def pseudo_randstr(l=12, cs=ALPHANUMUL):
	ret = ''
	for i in xrange(l):
		ret += cs[random.randint(0, len(cs)-1)]
	return ret

def args_to_users(args):
	from kn.leden.models import KnUser, KnGroup
	ret = set()
	had = set()
	for arg in args:
		tmp = KnGroup.objects.filter(name=arg)
		if len(tmp) != 0:
			for u in tmp[0].user_set.all():
				if u.pk in had:
					continue
				ret.add(u.knuser)
				had.add(u.pk)
			continue
		tmp = KnUser.objects.get(username=arg)
		if not tmp.pk in had:
			ret.add(tmp)
	return tuple(ret)

def print_table(data):
	ls = map(lambda x: max(map(lambda y: len(data[y][x]),
				   xrange(len(data)))),
		 xrange(len(data[0])))
	for d in data:
		l = ''
		for i, b in enumerate(d):
			l += b + (' ' * (ls[i] - len(b) + 1))
		print l

MAILDOMAIN = kn.leden.settings.MAILDOMAIN
LISTDOMAIN = 'lists.'+MAILDOMAIN

EMAIL_ALLOWED = frozenset(
		    map(lambda x: chr(ord('a') + x), xrange(26)) +
		    map(lambda x: chr(ord('A') + x), xrange(26)) +
		    map(lambda x: chr(ord('0') + x), xrange(10)) +
		    ['.', '-'])

GALLERY_PATH = '/var/galleries/kn/'
MEMBERS_HOME = '/home/kn/'
MEMBER_PHOTO_DIR = 'fotos/'
MEMBERS_ALBUM = 'per-lid'

GCAL_MAIN = 'vssp95jliss0lpr768ec9spbd8@group.calendar.google.com'
GCAL_UIT = '56ndj4j9iei03ahqa7fkrl566s@group.calendar.google.com'
GCAL_BD = '3p6k3ge8476t1bs5c20khat1uc@group.calendar.google.com'

MEMBER_GROUP = 'leden5'
DAYS_IN_YEAR = 365.242199

INST_RU = 2
INST_HAN = 1
