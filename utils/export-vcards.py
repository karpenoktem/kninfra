from __future__ import with_statement

import _import

import sys
from vcard import vcard
from kn.leden.models import KnUser, KnGroup

def export_vcards(group):
	g = KnGroup.objects.get(name=group)
	for u in g.user_set.all():
		u = u.knuser
		with open('%s.vcf' % u.username, 'w') as f:
			f.write(vcard(u.username))

if __name__ == '__main__':
	if len(sys.argv) != 2:
		 print 'usage: python export-vcards.py <group>'
		 sys.exit(-1)
	export_vcards(sys.argv[1])
