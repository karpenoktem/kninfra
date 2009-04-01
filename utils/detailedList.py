import _import

import sys
from common import *
from kn.leden.models import KnUser, KnGroup

g = KnGroup.objects.get(name=MEMBER_GROUP if len(sys.argv) == 1
					  else sys.argv[1])

for _u in g.user_set.all():
	u = _u.knuser
	print "%-13s %-17s %-1s %-10s %-25s %-26s %-8s %-10s %s" % \
				    (u.first_name,
				     u.last_name,
				     u.gender,
				     u.dateOfBirth,
				     u.get_primary_email(),
				     u.addr_street + ' ' + u.addr_number,
				     u.addr_zipCode,
				     u.addr_city,
				     u.telephone)
