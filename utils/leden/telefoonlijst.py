# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

from common import args_to_users
import sys

if sys.stdout.encoding is None:
    reload(sys)
    sys.setdefaultencoding('utf-8')


def fmt_date(d):
    if d is None:
        return ""
    return str(d.date())

fmt = "%35s%12s%12s%15s"
print fmt % ("NAME  ", "FROM  ", "UNTIL  ", "NUMBER  ")
for m in args_to_users(sys.argv[1:]):
    for nr in m.telephones:
        print fmt % (m.full_name,
                     fmt_date(nr['from']),
                     fmt_date(nr['until']),
                     nr['number'])
