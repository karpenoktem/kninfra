# vim: et:sta:bs=2:sw=4:
from __future__ import with_statement

import time
import math
import MySQLdb
from common import *

INTERVAL = 60*60*24*7
MAX_N = 12

def len_lb(l, x):
	""" returns the size of the lower bound of x in l assuming l
	    is sorted """
	i = glb_index(l, x)
	if l[i] <= x:
		return i + 1
	else:
		return i

def glb_index(l, x):
	""" finds the greatest lower bound of x in l assuming l is sorted """
	N = int(2**math.ceil(math.log(len(l),2)))
	c = N / 2
	w = N / 4
	while True:
		if c >= len(l) or l[c] >= x:
			c -= w
		else:
			c += w
		w /= 2
		if w == 0:
			break
	c = min(len(l)-1, c)
	while c != 0 and not l[c] <= x:
		c -= 1
	return c

def main():
	lut = dict()
	login = read_ssv_file('forum.login')
	db = MySQLdb.connect(host='localhost',
			     user=login[0],
			     passwd=login[2],
			     db=login[1])
	c = db.cursor()
	c.execute('SELECT poster, posted FROM posts')
	for poster, posted in c.fetchall():
		if not poster in lut:
			lut[poster] = list()
		lut[poster].append(posted)
	for l in lut.itervalues():
		l.sort()
	_from = time.time()
	data = dict()
	while True:
		m = 0
		for poster in lut:
			if not poster in data:
				data[poster] = list()
			n = len_lb(lut[poster], _from)
			m = max(n, m)
			data[poster].append(n)
		if m == 0:
			break
		_from -= INTERVAL
	users = sorted(data.keys(), cmp=lambda y,x: cmp(data[x][0], data[y][0]))
	data['others'] =[0]*len(data[users[0]])
	others = users[MAX_N:]
	for other in others:
		for i in xrange(len(data[other])):
			data['others'][i] += data[other][i]
		del(data[other])
	for user in reversed(['others']+ users[:MAX_N]):
		print ','.join(map(str,[user]+list(reversed(data[user]))))

if __name__ == '__main__':
	main()
