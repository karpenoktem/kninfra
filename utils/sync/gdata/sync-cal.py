import _import

from common import *
from cal_common import *

from kn.leden.models import OldKnUser, OldKnGroup
from iso8601 import parse_date
import gdata.calendar.service
from gdata.service import RequestError
import datetime
import atom

GCAL_SCHEME = 'http://schemas.google.com/gCal/2005#'

def acl_sync_cal(cs, cal, initial_role):
	acl_url = 'http://www.google.com/calendar'+ \
				     '/feeds/%s/acl/full' % cal
	feed = cs.GetCalendarAclFeed(acl_url)
	cur = dict()
	acc = set()
	for a_rule in feed.entry:
		if not a_rule.role.value == GCAL_SCHEME + initial_role:
			print "%s: unknown role: %s" % (a_rule.scope.value,
							a_rule.role.value)
			continue
		cur[a_rule.scope.value] = a_rule.GetEditLink().href
	for m in OldKnGroup.objects.get(name=MEMBER_GROUP).user_set.all():
		acc.add(m.email.lower())
		if m.email.lower() in cur: continue
		rule = gdata.calendar.CalendarAclEntry()
		rule.scope = gdata.calendar.Scope(value=m.email)
		rule.scope.type = 'user'
		rv = GCAL_SCHEME + initial_role
		rule.role = gdata.calendar.Role(value=rv)
		print 'Adding %s' % m.email
		try:
			cs.InsertAclEntry(rule, acl_url)
		except RequestError, e:
			if (e.args[0]['status'] == 409 and
			    e.args[0]['reason'] == 'Conflict'):
				print 'Warning: Version Conflict -- skipped'
			else:
				raise
	for n in frozenset(cur.iterkeys()) - acc:
		print "Deleting stray %s" % n
		cs.DeleteAclEntry(cur[n])

def icaldate(d):
	return "%s%s%s" % (d.year,
			   str(d.month).zfill(2),
			   str(d.day).zfill(2))

def sync_bd(cs, cal):
	cal_uri = '/calendar/feeds/%s/private/full' % cal
	now = datetime.datetime.now().date()
	now2 = datetime.date(now.year + 1, now.month, now.day)
	query = gdata.calendar.service.CalendarEventQuery(cal, 
			'private', 'full')
	query.start_min = str(now)
	query.start_max = str(now2)
	todo = set(filter(lambda x: not x.dateOfBirth is None,
			  OldKnUser.objects.all()))
	fn_lut = dict()
	rd_lut = dict()
	for m in todo:
		fn_lut[m.get_full_name()] = m
		rd_lut[m.get_full_name()] = ('DTSTART;VALUE=DATE:%s\n'+
			 		     'DTEND;VALUE=DATE:%s\n'+
					     'RRULE:FREQ=YEARLY\n') % (
						icaldate(m.dateOfBirth),
						icaldate(m.dateOfBirth +
							datetime.timedelta(1)))
	feed = cs.CalendarQuery(query)
	while True:
		for event in feed.entry:
			if not event.title.text in fn_lut:
				print "STRAY EVENT: %s" % event.title.text
				continue
			if not fn_lut[event.title.text] in todo:
				print 'DOUBLE EVENT: %s' % event.title.text
				continue
			todo.remove(fn_lut[event.title.text])
			if not hasattr(event, 'recurrence'):
				print 'RECC-less EVENT: %s' % event.title.text
				continue
			if event.recurrence.text != rd_lut[event.title.text]:
				print "RECC: %s %s != %s" % (
						event.title.text,
						rd_lut[event.title.text],
						event.recurrence.text)
				continue
		if feed.GetNextLink() is None:
			break
		feed = cs.Query(feed.GetNextLink().href,
			converter=gdata.calendar.CalendarEventFeedFromString)
	for m in todo:
		if m.dateOfBirth is None:
			continue
		event = gdata.calendar.CalendarEventEntry()
		event.title = atom.Title(text=m.get_full_name())
		event.content = atom.Content(
			text='Verjaardag van %s'%m.get_full_name())
		event.recurrence = gdata.calendar.Recurrence(
					text=rd_lut[m.get_full_name()])
		cs.InsertEvent(event, cal_uri)
		print 'Added %s' % m.get_full_name()

if __name__ == '__main__':
	cs = get_cs()
	print 'BIRTHDAY ACCESS'
	acl_sync_cal(cs, GCAL_BD, 'read')
	print 'UIT AGENDA'
	acl_sync_cal(cs, GCAL_UIT, 'editor')
	print 'BIRTHDAYS'
	sync_bd(cs, GCAL_BD)

