import _import

import sys
from kn.poll.models import Poll, Question, AnswerSet, Answer, Filling

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
	N = 0
	for q in reversed(poll.question_set.all()):
		N += 1
		for a in q.filling_set.all():
			if not a.answer in lut:
				lut[a.answer] = 0
			lut[a.answer] += N
	for a, n in sorted(lut.items(), cmp=lambda x,y: cmp(y[1], x[1])):
		print "%4s %s" % (n, a)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'usage: python top-pick.py <poll>'
		sys.exit(-1)
	main(sys.argv[1])
