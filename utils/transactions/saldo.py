# vim: et:sta:bs=2:sw=4:
# -*- coding: utf-8 -*
import _import

from kn.leden.models import OldKnUser, Transaction

def main():
    u2t = dict()
    for t in Transaction.objects.order_by('date').all():
        if not t.user in u2t:
            u2t[t.user] = list()
        u2t[t.user].append(t)
    for u in u2t.iterkeys():
        s = sum(map(lambda u: u.value, u2t[u]))
        if s == 0: continue

        cs = 0
        for i, t in enumerate(u2t[u]):
            if cs == 0:
                lastZero_index = i
            cs += t.value

        print '  %s' % u.full_name()
        for i in xrange(lastZero_index, len(u2t[u])):
            t = u2t[u][i]
            print u' %s €%s %s %s' % (t.date,
                          t.value,
                          t.type,
                          t.description)
        print u'         totaal €%s' % s
        print

if __name__ == '__main__':
    main()
