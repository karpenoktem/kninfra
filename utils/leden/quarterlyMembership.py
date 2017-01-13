# vim: et:sta:bs=2:sw=4:

import _import

from common import *
import kn.leden.entities as Es

import datetime


def main():
    leden = Es.by_name('leden')
    lut = {}
    id2name = {}
    for m in Es.users():
        if not m.name: continue
        lut[str(m.name)] = set()
        id2name[m._id] = str(m.name)
    max_q = Es.date_to_year(Es.now()) * 4
    for q in xrange(1, max_q + 1):
        start, end = Es.quarter_to_range(q)
        for m in leden.get_rrelated(_from=start, until=end, how=None,
                    deref_who=False, deref_with=False, deref_how=False):
            lut[id2name[m['who']]].add(q)
    for i, name in enumerate(sorted(id2name.itervalues())):
        if i % 20 == 0:
            print
            print '%20s %s' % ('year', ' '.join([str(((q - 1) / 4) + 1 ).ljust(7)
                                    for q in xrange(1, max_q + 1, 4)]))
            print '%20s %s' % ('quarter', ' '.join([str(((q - 1) % 4) + 1 )
                                    for q in xrange(1, max_q + 1)]))
        print '%-20s %s' % (name, ' '.join(['*' if q in lut[name] else ' '
                                for q in xrange(1, max_q + 1)]))


if __name__ == '__main__':
    main()
