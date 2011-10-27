# vim: et:sta:bs=2:sw=4:
import _import
import datetime
import sys

import kn.leden.entities as Es
from kn.settings import DT_MIN, DT_MAX
from kn.leden.mongo import _id
from kn.leden.date import now
from kn.planning.entities import Pool, Worker, Vacancy

pools = dict()
for p in Pool.all():
	pools[p.name] = p

workers = dict()
for w in Worker.all():
	workers[w.get_user()] = w

dt = now()
for type in ['tappers', 'bestuur', 'barco', 'draai']:
	poolid = _id(pools[type])
	group = Es.by_name(type)
	relations = group.get_rrelated(None, dt, dt, True, None, None)
	for gm in relations:
		if gm['who'] in workers:
			if poolid not in workers[gm['who']].pools:
				print '%s -> %s' % (gm['who'].name, type)
				workers[gm['who']].pools.append(poolid)
				workers[gm['who']].save()
		else:
			print '%s -> %s' % (gm['who'].name, type)
			workers[gm['who']] = Worker({
				'pools': [ poolid ],
				'user': _id(gm['who'])})
			workers[gm['who']].save()