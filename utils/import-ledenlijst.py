from __future__ import with_statement

#
# A hopefully one-time-script to import the member database
# from csv
#

import datetime
from kn.leden.models import Member, EduInstitute, Study
from django.contrib.auth.models import User
from cStringIO import StringIO

def parse_csvline(s):
	b = StringIO()
	q = False
	e = False
	for c in s:
		if e:
			b.write(c)
			e = False
			continue
		if c == "\"":
			q = not q
		elif not q and c == ",":
			yield b.getvalue()
			b = StringIO()
		elif c == "\\":
			e = True
		else:
			b.write(c)
	yield b.getvalue()

def sanitize_number(s):
	r = StringIO()
	for c in s:
		if ord('0') > ord(c) or ord('9') < ord(c): continue
		r.write(c)
	if r.getvalue() == '': return None
	return int(r.getvalue())

def sanitize_login(s):
	s = s.lower()
	r = StringIO()
	for c in s:
		if ord('a') > ord(c) or ord('z') < ord(c): continue
		r.write(c)
	return r.getvalue()

def usernames(voor, achter):
	for i in xrange(len(achter)):
		r = voor + achter[:i]
		yield sanitize_login(r)

def parseDate(date):
	sep = None
	MONTHS = {'jan':1, 'feb':2, 'mar':3, 'apr':4, 'mei':5, 'jun':6,
		  'jul':7, 'aug':8, 'sep':9, 'okt':10, 'nov':11, 'dec':12,
		  'oct':10, 'may':5}
	for i in ('-', '/'):
		if i in date:
			sep = i
	if sep == None:
		return None
	bits = date.split(sep)
	if sep == '/':
		bits[0], bits[1] = bits[1], bits[0]
	if len(bits) != 3: return None
	if len(bits[2]) != 4: bits[2] = '19'+bits[2]
	try:
		bits[1] = int(bits[1])
	except ValueError:
		bits[1] = bits[1].lower()
		if bits[1] in MONTHS:
			bits[1] = MONTHS[bits[1]]
	return datetime.date(int(bits[2]), int(bits[1]), int(bits[0]))

def ledenlijst_from_csv(f):
	inst_map = {'RU': 'Radboud Universiteit Nijmegen',
		    'HAN': 'HAN Nijmegen',
		    'Fontys Hs': 'Fontys Hoge School',
		    'Radboud Universiteit Nijmegen': 'Radboud Universiteit Nijmegen'}

	while True:
		l = f.readline()
		if l == '': break
		l = l[:-1]
		betaald, voorNaam, achterNaam, _geboorteDatum, a_straat, \
			a_nummer, a_postcode, a_plaats, email, \
			telefoonNummer, instelling, studie, studentNummer, \
			_lidSinds = parse_csvline(l)
		if voorNaam == achterNaam == '':
			print "DBG Skipping empty line"
			continue
		if len(User.objects.filter(email=email)) != 0:
			print "%s already in database" % email
			continue
		for username in usernames(voorNaam, achterNaam):
			if len(User.objects.filter(username=username)) == 0: break
		if len(User.objects.filter(username=username)) != 0:
			print voorNaam, achterNaam, username
			assert False
		u = User(username=username,
		         email=email,
			 first_name=voorNaam,
			 last_name=achterNaam)
		lidSinds = parseDate(_lidSinds)
		geboorteDatum = parseDate(_geboorteDatum)
		if _geboorteDatum != '' and geboorteDatum is None:
			print 'WAR Couldn\'t parse date %s' % _geboorteDatum
		if _lidSinds != '' and lidSinds is None:
			print 'WAR Couldn\'t parse date %s' % _lidSinds
		telefoonNummer = sanitize_number(telefoonNummer)
		studentNummer = sanitize_number(studentNummer)
		if not instelling in inst_map:
			print 'WAR Instelling %s not found' % instelling
		else:
			if instelling == '':
				inst = None
			else:
				try:
					inst = EduInstitute.objects.get(name=instelling)
				except EduInstitute.DoesNotExist:
					inst = EduInstitute(name=instelling)
					inst.save()
		if studie == '':
			stud = None
		else:
			try:
				stud = Study.objects.get(name=studie)
			except Study.DoesNotExist:
				stud = Study(name=studie)
				stud.save()
		u.save()
		m = Member(user=u,
			   dateOfBirth=geboorteDatum,
			   addr_street=a_straat,
			   addr_number=a_nummer,
			   addr_zipCode=a_postcode,
			   addr_city=a_plaats,
			   telephone=telefoonNummer,
			   studentNumber=studentNummer,
			   dateJoined=lidSinds,
			   institute=inst,
			   study=stud)
		m.save()

if __name__ == '__main__':
	with open('ledenlijst.csv') as f:
		ledenlijst_from_csv(f)
