import _import
from common import *

from kn.leden.models import Study, KnGroup

leden = frozenset(map(lambda x: x.oldknuser,
	          KnGroup.objects.get(name=MEMBER_GROUP).user_set.all()))

for s in Study.objects.all():
	sm = frozenset(s.oldknuser_set.all()).intersection(leden)
	print len(sm), s
