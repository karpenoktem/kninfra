# vim: et:sta:bs=2:sw=4:
import _import
from common import *

from kn.leden.models import Study, OldKnGroup

leden = frozenset(map(lambda x: x.oldknuser,
              OldKnGroup.objects.get(name=MEMBER_GROUP).user_set.all()))

for s in Study.objects.all():
    sm = frozenset(s.oldknuser_set.all()).intersection(leden)
    print len(sm), s