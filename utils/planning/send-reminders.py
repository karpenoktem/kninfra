import _import
import datetime
import sys

import locale

import kn.leden.entities as Es
from kn.settings import DT_MIN, DT_MAX
from kn.leden.mongo import _id
from kn.planning.entities import Pool, Worker, Vacancy

locale.setlocale(locale.LC_ALL, 'nl_NL')

msgfmt = """Dag %(firstName)s,

Denk je eraan dat je %(date)s moet tappen vanaf %(time)s?

Met geautomatiseerde groet,
De BarCo"""

vacancies = Vacancy.all_needing_reminder()
for vacancy in vacancies:
	if vacancy.assignee:
		to = vacancy.assignee.get_user()
	else: 
		to = Es.by_name('jesper2')
	msg = msgfmt % {
		'firstName': to.first_name,
		'date': vacancy.date.strftime('%A %m %B'),
		'time': vacancy.begin_time
	}
	print msg
	vacancy.reminder_sent = True
#	vacancy.save()
