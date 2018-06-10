# vim: et:sta:bs=2:sw=4:

import _import  # noqa: F401

from django.utils import six
from django.utils.six.moves import range

ALPHA = 'qwertyuiopasdfghjklzxcvbnm'
NUM = '1234567890'
ALPHANUMUL = ALPHA + ALPHA.upper() + NUM


"""
Given a list of names,
returns the users which are
  0.  named in this list,
  1.  members of groups named in this list,
  2.  members of groups of members of groups named in this list,
       ...

and raises a NotImplemtedError when another type of
Entity then "user" or "group" is encountered.

Cycles are accounted for.
"""


def args_to_users(args):
    import kn.leden.entities as Es
    ret = set()  # set of Entities found
    had = set()  # set of Entities dealt with
    todo = set()  # set of Entities to be dealt with
    todo.update(six.itervalues(Es.by_names(args)))
    while len(todo) > 0:
        e = todo.pop()
        if e in had:
            continue
        had.add(e)
        if e.type == "user":
            ret.add(e)
            continue
        if e.type != "group":
            raise NotImplementedError()
        todo.update(e.get_members())
    return tuple(ret)


def print_table(data, separator=' '):
    if len(data) == 0:
        return
    ls = [max([len(data[y][x])
               for y in range(len(data))])
          for x in range(len(data[0]))]
    for d in data:
        line = ''
        for i, b in enumerate(d):
            line += b + (' ' * (ls[i] - len(b))) + separator
        print(line)
