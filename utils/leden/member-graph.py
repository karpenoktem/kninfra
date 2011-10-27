# vim: et:sta:bs=2:sw=4:
import _import
import datetime
import sys
from kn.leden.models import OldKnUser, OldKnGroup

def date_to_year(dt):
    if dt.month < 9:
        return max(1, dt.year - 2004)
    return max(1, dt.year - 2003)

def main():
    lut = dict()
    members = set()
    N = 0
    while True:
        N += 1
        try:
            g = OldKnGroup.objects.get(name='leden%s' % N)
        except OldKnGroup.DoesNotExist:
            break
        M = [m.username for m in g.user_set.all()]
        lut[N] = frozenset(M)
        members.update(M)
    cur = set()
    had = set()
    ret = []
    y = 0
    for m in OldKnUser.objects.order_by('dateJoined'):
        if not m.username in members:
            continue
        if y != date_to_year(m.dateJoined):
            y = date_to_year(m.dateJoined)
            cur = set(filter(lambda x: x in lut[y], cur))
            cur.update(filter(lambda x: x in had, lut[y]))
        cur.add(m.username)
        had.add(m.username)
        ret.append((m.dateJoined, len(cur)))
    idx = filter(lambda i: ret[i-1][0] != ret[i][0],
        xrange(1, len(ret)))
    for dj, N in map(lambda i: ret[i-1], idx) + [ret[-1]]:
        print '%s' % (dj-datetime.date(2004,9,1)).days, N

if __name__ == '__main__':
    if sys.stdout.encoding is None:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    main()