# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import sys

from common import args_to_users
from six.moves import reload_module

if sys.stdout.encoding is None:
    reload_module(sys)
    sys.setdefaultencoding('utf-8')


def fmt_date(d):
    if d is None:
        return ""
    return str(d.date())


fmt = '%35s %14s'
print(fmt % ('NAME', 'NUMBER'))
for m in args_to_users(sys.argv[1:]):
    print(fmt % (m.full_name, m.telephone))
