# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import sys
from kn.poll.models import Poll

# Some polls look like:
#  Poll: what's your top 5
#  Question 1: what's your first pick
#  Question 2: what's your second pick
#  ..
#
# This script awards (N - n) points to an answer if it is filed to the n-th
# question out of N.


def main(poll):
    poll = Poll.objects.get(name=poll)
    lut = dict()
    lastUserAnswerVote = dict()
    N = 0
    for q in reversed(poll.question_set.all()):
        N += 1
        for a in q.filling_set.all():
            if a.user not in lastUserAnswerVote:
                lastUserAnswerVote[a.user] = dict()
            if a.answer in lastUserAnswerVote[a.user]:
                # user heeft hier al op gestemd, we halen de punten van zijn eerdere vote weg
                # (dat is namelijk een lagere vote) en tellen deze vote er zometeen bij op
                lut[a.answer] -= lastUserAnswerVote[a.user][a.answer]
            if a.answer not in lut:
                lut[a.answer] = 0
            lut[a.answer] += N
            lastUserAnswerVote[a.user][a.answer] = N
    for a, n in sorted(lut.items(), cmp=lambda x, y: cmp(y[1], x[1])):
        print "%4s %s" % (n, a)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: python top-pick.py <poll>'
        sys.exit(-1)
    main(sys.argv[1])
