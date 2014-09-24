import _import

import kn.leden.entities as Es

import subprocess
import pyx
import sys

def generate():
    ret = []
    events = []
    for rel in Es.query_relations(_with=Es.id_by_name('leden'), how=None):
        events.append((max(rel['from'], Es.DT_MIN), True))
        if rel['until'] != Es.DT_MAX:
            events.append((rel['until'], False))
    N = 0
    old_days = -1
    old_N = None
    for when, what in sorted(events, key=lambda x: x[0]):
        N += 1 if what else -1
        days = (when - Es.DT_MIN).days
        if old_days != days:
            if old_N:
                ret.append([old_days, old_N])
                print old_days, old_N
            old_days = days
            old_N = N
    ret.append([days, N])
    ret = [(1 + days / 365.242, N) for days, N in ret]
    return ret

def main():
    ret = generate()
    g = pyx.graph.graphxy(width=10, x=pyx.graph.axis.linear(min=1,
                    painter=pyx.graph.axis.painter.regular(
                            gridattrs=[pyx.attr.changelist([
                                pyx.color.gray(0.8)])])))
    g.plot(pyx.graph.data.points(ret,x=1,y=2),
                [pyx.graph.style.symbol(size=0.03,
                        symbol=pyx.graph.style.symbol.plus)])
    g.writePDFfile('member-graph' if len(sys.argv) <= 1
                            else sys.argv[1])

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
