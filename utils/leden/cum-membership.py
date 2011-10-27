# vim: et:sta:bs=2:sw=4:
import _import
from kn.leden.models import OldKnUser, OldKnGroup
from common import *

def main():
    N = 0
    while True:
        N += 1
        try:
            g = OldKnGroup.objects.get(name='leden%s'%N)
        except OldKnGroup.DoesNotExist:
            break
    data = [[0 for i in xrange(1,N)] for j in xrange(1,N)]
    groups = list()
    for i in xrange(1,N):
        groups.append(map(lambda x: x.oldknuser,
            OldKnGroup.objects.get(
            name='leden%s'%i).user_set.all()))
    users = reduce(lambda x,y: x+y, groups, [])
    groups = map(frozenset, groups)
    for user in frozenset(users):
        first = None
        for i in xrange(1,N):
            if user in groups[i-1]:
                if first is None:
                    first = i
                data[first-1][i-1] += 1
    for r in data:
        print '\t'.join(map(str, r))

if __name__ == '__main__':
    main()