import _import

import sys
import datetime

import kn.leden.entities as Es
from kn.settings import DT_MIN, DT_MAX
from kn.leden.mongo import _id
from kn.planning.entities import Pool, Worker, Event, Vacancy

def hm2s(hours, minutes=0):
	return (hours * 60 + minutes) * 60

typePeriods = {
	'tappers': [[hm2s(20, 30), hm2s(23), 'eerste dienst'],
                [hm2s(23), hm2s(25), 'tweede dienst'],
                [hm2s(25), hm2s(28), 'derde dienst']],
	'bestuur': [[hm2s(20, 30), hm2s(24), 'openen'],
                [hm2s(24), hm2s(28), 'sluiten']],
	'draai': [[hm2s(20, 45), hm2s(23), 'openen'],
                [hm2s(23), hm2s(24), 'prime-time'],
                [hm2s(24), hm2s(25), 'sluiten']]}

day = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')

e = Event({
	'name': 'Borrel',
	'date': day })
e.save()

for _type, periods in typePeriods.items():
	pool = Pool.by_name(_type)
	for period in periods:
		v = Vacancy({
			'name': period[2],
			'event': _id(e),
			'begin': day + datetime.timedelta(seconds=period[0]),
			'end': day + datetime.timedelta(seconds=period[1]),
			'pool': _id(pool),
			'assignee': None,
		})
		print v._data
		v.save()
