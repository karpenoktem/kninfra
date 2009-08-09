import _import

from common import *
from kn.leden.models import OldKnGroup
import sys

for m in args_to_users(sys.argv[1:]):
	print "%15s%20s%15s" % (m.first_name,
				m.last_name,
				m.oldknuser.telephone)
