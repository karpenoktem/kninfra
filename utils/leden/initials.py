# vim: et:sta:bs=2:sw=4:
import _import

from common import *
from kn.leden.models import OldKnGroup

for m in OldKnGroup.objects.get(name=MEMBER_GROUP).user_set.all():
	print m.first_name[0] + m.last_name[0]
