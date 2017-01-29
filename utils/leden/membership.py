# vim: et:sta:bs=2:sw=4:
from __future__ import print_function

import _import  # noqa: F401

from django.utils import six
from django.utils.six.moves import range

import sys
from common import args_to_users
import kn.leden.entities as Es

users = dict()
if len(sys.argv) == 1:
    _users = Es.users()
else:
    _users = args_to_users(sys.argv[1:])

for m in _users:
    users[str(m.name)] = set()

i = 0
while True:
    i += 1
    g = Es.by_name('leden%s' % i)
    if g is None:
        break
    for m in g.get_members():
        if str(m.name) in users:
            users[str(m.name)].add(i)
nyears = i - 1
N = 0

for m, ys in six.iteritems(users):
    N += 1
    if N % 20 == 0:
        print("%15s" % '', end=' ')
        for y in range(1, nyears + 1):
            print(y, end=' ')
        print()
    print("%15s" % m, end=' ')
    for y in range(1, nyears + 1):
        print('*' if y in ys else ' ', end=' ')
    print()
