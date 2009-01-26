import _import

from common import *
from kn.leden.models import KnGroup

for m in KnGroup.objects.get(name=MEMBER_GROUP).user_set.order_by(
		'first_name').all():
	print "%15s%20s%15s" % (m.first_name,
				m.last_name,
				m.knuser.telephone)
