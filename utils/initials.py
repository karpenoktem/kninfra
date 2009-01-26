import _import

from common import *
from kn.leden.models import KnGroup

for m in KnGroup.objects.get(name=MEMBER_GROUP).user_set.all():
	print m.first_name[0] + m.last_name[0]
