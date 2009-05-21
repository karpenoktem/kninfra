import _import
from django import db
from kn.poll.models import *
from django.contrib.auth.models import User

def main():
	plut = dict()
	qlut = dict()
	alut = dict()
	ulut = dict()
	for q in Question.objects.all():
		if not q.poll_id in plut:
			plut[q.poll_id] = list()
		plut[q.poll_id].append(q)
	for f in Filling.objects.all():
		if not f.question_id in qlut:
			qlut[f.question_id] = list()
		qlut[f.question_id].append(f)
	for a in Answer.objects.all():
		alut[a.pk] = a
	for u in User.objects.all():
		ulut[u.pk] = u
	for poll in Poll.objects.all():
		print poll
		for q in plut[poll.pk]:
			lut = dict()
			if not q.id in qlut:
				continue
			for f in qlut[q.id]:
				if not f.answer_id in lut:
					lut[f.answer_id] = list()
				lut[f.answer_id].append(f.user_id)
			tmp = sorted(lut.iteritems(),
				     cmp=lambda x,y: cmp(len(y[1]),
							 len(x[1])))
			if len(tmp) == 0:
				continue
			print " %s" %q
			for a, us in tmp:
				us = map(lambda x: ulut[x].username, us)
				print '  %-25s %s %s' % (alut[a], len(us), ', '.join(us))

if __name__ == '__main__':
	main()
