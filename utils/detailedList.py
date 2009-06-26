import _import

import sys
from common import *
from kn.leden.models import KnUser, KnGroup

if sys.stdout.encoding is None:
	reload(sys)
	sys.setdefaultencoding('utf-8')
data = []
for u in args_to_users(sys.argv[1:]):
	data.append((
		u.first_name,
		u.last_name,
		u.gender,
		u.studentNumber,
		u.institute,
		u.study,
		u.dateOfBirth,
		u.dateJoined,
		u.primary_email,
		u.addr_street,
		u.addr_number,
		u.addr_zipCode,
		u.addr_city,
		u.telephone))
data = map(lambda r: map(lambda x: unicode(x), r), data)
print_table(data)
