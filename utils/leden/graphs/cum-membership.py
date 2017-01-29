# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import kn.leden.entities as Es
from functools import reduce

from django.utils.six.moves import range


def main():
    N = 0
    while True:
        N += 1
        g = Es.by_name('leden%s' % N)
        if g is None:
            break
    data = [[0 for i in range(1, N)] for j in range(1, N)]
    groups = list()
    for i in range(1, N):
        groups.append(Es.by_name('leden%s' % i).get_members())
    users = reduce(lambda x, y: x + y, groups, [])
    groups = map(frozenset, groups)
    for user in frozenset(users):
        first = None
        for i in range(1, N):
            if user in groups[i - 1]:
                if first is None:
                    first = i
                data[first - 1][i - 1] += 1
    for r in data:
        print('\t'.join(map(str, r)))
    print()
    for y in range(len(data)):
        m = data[y][y]
        row = []
        for sy in range(len(data) - y):
            row.append(data[y][y + sy] * 100 / m)
        print('\t'.join(map(str, row)))


if __name__ == '__main__':
    main()
