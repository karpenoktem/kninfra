# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import sys
from optparse import OptionParser
from common import args_to_users, print_table

op = OptionParser()
op.add_option('-s', '--separator', dest='separator', default=' ',
              metavar='CHAR', type=str,
              help="The seoarator between spaces")
options, args = op.parse_args()

if sys.stdout.encoding is None:
    reload(sys)
    sys.setdefaultencoding('utf-8')
data = []
for u in args_to_users(args):
    data.append((
        u.first_name,
        u.last_name,
        u.studentNumber,
        u.institute,
        u.study,
        u.dateOfBirth,
        u.dateJoined,
        u.primary_email,
        u.addr_street,
        u.addr_number,
        u.addr_zipCode,
        u.addr_city,
        u.telephone))
data = map(lambda r: map(lambda x: unicode(x), r), data)
print_table(data, separator=options.separator)
