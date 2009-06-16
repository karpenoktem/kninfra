import _import

import sys
from common import *
from kn.leden.models import KnUser, KnGroup

for u in args_to_users(sys.argv[1:]):
	print "%-13s %-17s %-1s %-10s %-25s %-26s %-8s %-10s %s" % \
				    (u.first_name,
				     u.last_name,
				     u.gender,
				     u.dateOfBirth,
				     u.primary_email,
				     u.addr_street + ' ' + u.addr_number,
				     u.addr_zipCode,
				     u.addr_city,
				     u.telephone)
