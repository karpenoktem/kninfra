# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

from common import MEMBER_GROUP

import kn.leden.entities as Es

for m in Es.by_name(MEMBER_GROUP).get_members():
    print(m.first_name[0] + m.last_name[0])
