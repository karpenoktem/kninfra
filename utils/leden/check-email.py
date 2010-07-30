from __future__ import with_statement

import _import
import sys
from datetime import date, datetime
from kn.leden.models import OldKnUser
from common import *

DAYS_IN_YEAR = 365.242199

def check_email():
	with open('check-email.template', 'r') as f:
		templ = f.read()

	for m in args_to_users(sys.argv[1:]):
		msgs = list()
		if m.dateJoined is None:
			msgs.append("de datum van toetreden is onbekend")
		else:
			if m.dateJoined < date(2004, 4, 1):
				msgs.append("je bent toegetreden voor "+
					    "de constitutie")
		if m.dateOfBirth is None:
			msgs.append("je geboortedatum is onbekend")
		else:
			age = (datetime.now().date() - m.dateOfBirth).days \
					/ DAYS_IN_YEAR
			if age < 15:
				msgs.append("je bent jonger dan 15")
			elif age > 40:
				msgs.append("je bent ouder dan 40")
		if m.addr_street == '':
			msgs.append("we missen de straat van je adres")
		if m.addr_zipCode == '':
			msgs.append("we missen de postcode van je adres")
		if m.addr_number == '':
			msgs.append("we missen het huisnummer van je adres")
		if m.addr_city == '':
			msgs.append("van adres is geen plaats bekend")
		if m.telephone is None or m.telephone == '':
			msgs.append("jouw telefoonnummer is onbekend")
		if m.studentNumber is None:
			msgs.append("jouw studentnummer is onbekend")
		elif len(m.studentNumber) != 7:
			msgs.append("jouw studentnummer lijkt fout")
		if len(msgs) != 0:
			extra = 'Een paar zaken vallen op:\n'
			for i, msg in enumerate(msgs):
				if i == 0: msg = msg.capitalize()
				extra += ' - %s' % msg
				if i == len(msgs) - 2: extra += ' en\n'
				elif i == len(msgs) - 1: extra += '.\n'
				else: extra += ';\n'
		else:
			extra = ''
		em = templ % (
			{'username': m.username,
			 'firstName': m.first_name,
			 'lastName': m.last_name,
			 'fullName': m.full_name(),
			 'gender': ('onbekend' if m.gender is None
				else {'m': 'man',
				      'v': 'vrouw'}.get(m.gender, '?')),
			 'dateOfBirth': ('onbekend' if m.dateOfBirth is None
				else str(m.dateOfBirth)),
			 'dateJoined': ('onbekend' if m.dateJoined is None
				else str(m.dateJoined)),
			 'email': m.email,
			 'telephone': ('onbekend' if m.telephone is None
				else m.telephone),
			 'addr_street': ('onbekend' if m.telephone is None
				else m.addr_street),
			 'addr_number': ('onbekend' if m.telephone is None
				else m.addr_number),
			 'addr_city': ('onbekend' if m.telephone is None
				else m.addr_city),
			 'addr_zipCode': ('onbekend' if m.telephone is None
				else m.addr_zipCode),
			 'institute': ('onbekend' if m.telephone is None
				else m.institute),
			 'study': ('onbekend' if m.telephone is None
				else m.study),
			 'studentNumber': ('onbekend' if m.telephone is None
				else m.studentNumber),
			 'extra': extra
			})
		print m
		m.email_user('Controle Karpe Noktem ledenadministratie',
		     em, from_email='secretaris@karpenoktem.nl') 

if __name__ == '__main__':
	check_email()
