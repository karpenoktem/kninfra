# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import kn.poll.entities as poll_Es


def main():
    for p in poll_Es.all_polls():
        print p.humanName
        counts = [[0] * (len(q[1]) + 1) for q in p.questions]
        for f in p.fillings():
            for n, a in enumerate(f.answers):
                counts[n][len(p.questions[n][1])+1 if a is None else a] += 1
        for n, q in enumerate(p.questions):
            print ' %s' % q[0]
            for m, a in enumerate(q[1]):
                print '  %-50s %s' % (a, counts[n][m])
        print

if __name__ == '__main__':
    main()
