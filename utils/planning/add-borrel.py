import _import
import datetime
import sys

import kn.leden.entities as Es
from kn.settings import DT_MIN, DT_MAX
from kn.leden.mongo import _id
from kn.planning.entities import Pool, Worker, Event, Vacancy

def hm2s(hours, minutes=0):
	return (hours * 60 + minutes) * 60

day = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
pool = Pool.by_name('tappers')

e = Event({
	'name': 'Borrel',
	'date': day
})
e.save()

vacancies = list()
for period in [[hm2s(20, 30), hm2s(23)], [hm2s(23), hm2s(25)], [hm2s(25), hm2s(28)]]:
	v = Vacancy({
		'name': 'Borrel',
		'event': _id(e),
		'begin': day + datetime.timedelta(seconds=period[0]),
		'end': day + datetime.timedelta(seconds=period[1]),
		'pool': _id(pool),
		'assignee': None,
	})
	print v._data
	v.save()
