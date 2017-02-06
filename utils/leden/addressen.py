# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import sys

from common import args_to_users

if sys.stdout.encoding is None:
    reload(sys)
    sys.setdefaultencoding('utf-8')

for m in args_to_users(sys.argv[1:]):
    print("%-35s %-7s %-16s %s" % (m.primary_address.get('street'),
                                   m.primary_address.get('number'),
                                   m.primary_address.get('city'),
                                   m.name))
