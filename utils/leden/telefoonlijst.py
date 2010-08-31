import _import

from common import *
import sys

if sys.stdout.encoding is None:
	reload(sys)
	sys.setdefaultencoding('utf-8')

for m in args_to_users(sys.argv[1:]):
	print "%15s%20s%15s" % (m.first_name,
				m.last_name,
				m.oldknuser.telephone)
