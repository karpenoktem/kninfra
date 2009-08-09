from __future__ import with_statement

import _import
import MySQLdb
from common import *
from kn.leden.models import OldKnGroup, OldKnUser

def forum_email():
	with open('forum-email.template', 'r') as f:
		templ = f.read()
	pwd_lut = dict()
	with open('temp-pwds', 'r') as f:
		while True:
			l = f.readline()
			if l == '': break
			l = l[:-1]
			usr, pwd = l.split(' ')
			pwd_lut[usr] = pwd
	l5 = frozenset(map(lambda x: x.username, OldKnGroup.objects.get(
		name=MEMBER_GROUP).user_set.all()))
	login = read_ssv_file('forum.login')
	db = MySQLdb.connect(host='localhost',
			     user=login[0],
			     passwd=login[2],
			     db=login[1])
	c = db.cursor()
	c.execute('SELECT username FROM users WHERE last_visit=0')
	toEmail = set()
	for username, in c.fetchall():
		if not username in l5:
			continue
		toEmail.add(username)
	for username in toEmail:
		m = OldKnUser.objects.get(username=username)
		txt = templ % ({'fullName': m.get_full_name(),
				'password': pwd_lut[m.username],
				'userName': username})
		m.email_user(
			'Karpe Noktem forum',
			txt, from_email='bas@karpenoktem.nl')
		print username

if __name__ == '__main__':
	forum_email()
