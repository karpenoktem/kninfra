# vim: et:sta:bs=2:sw=4:
import _import

from common import *
import sys

if sys.stdout.encoding is None:
    reload(sys)
    sys.setdefaultencoding('utf-8')

def fmt_date(d):
    if d==None:
        return ""
    return str(d)

fmt = "%35r%10s%10s%15s"
print fmt % ("NAME  ", "FROM  ", "UNTIL  ", "NUMBER  ")
for m in args_to_users(sys.argv[1:]):
    for nr in m.telephones:
        print  fmt % (m.full_name,
                fmt_date(nr['from']),
                fmt_date(nr['until']),
                nr['number'])
