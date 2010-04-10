from __future__ import with_statement

import _import
import sys
import cStringIO
from datetime import date, datetime
from kn.leden.models import OldKnUser, OldKnGroup
from common import *

def group_email():
	with open('group-email.template', 'r') as f:
		templ = f.read()
	Gs = OldKnGroup.objects.all()
	glut = dict()
	plut = dict()
	for g in Gs:
		glut[g.name] = g
		if not g.parent_id in plut:
			plut[g.parent_id] = list()
		plut[g.parent_id].append(g)
	for g in Gs:
		if not g.id in plut:
			continue
		plut[g.id].sort(cmp=lambda x,y: cmp(x.humanName, y.humanName))
	tree = list()
	stack = [(0, glut['besturen']),
		 (0, glut['lists']),
		 (0, glut['groepen']),
		 (0, glut['comms'])]
	had = set(stack)
	while stack:
		d, g = stack.pop()
		tree.append((d, g))
		if not g.id in plut:
			continue
		for g2 in reversed(plut[g.id]):
			if g2 in had:
				continue
			if g2.isHidden:
				continue
			stack.append((d+1, g2))
			had.add(g2)
	for m in args_to_users(sys.argv[1:]):
		mlut = set(m.groups.all())
		s = cStringIO.StringIO()
		for d, g in tree:
			s.write("%s %s%s\n" % (
				"   " * d, g.humanName,
				' *' if g in mlut else ''))
		s2 = cStringIO.StringIO()
		for _s in m.oldseat_set.all():
			s2.write("  %s %s %s\n" % (_s.humanName,
						 _s.group.genitive_prefix,
						 _s.group.humanName))
		stext = s2.getvalue()
		stext = '(geen)' if stext == '' else stext
		em = templ % {'fullName': m.get_full_name(),
			      'seats': stext,
			      'tree': s.getvalue()}
		m.email_user('Overzicht groepen, commissies en e-maillijsten',
		     em, from_email='secretaris@karpenoktem.nl') 

if __name__ == '__main__':
	group_email()
