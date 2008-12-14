import _import

from common import *

from kn.leden.models import KnUser
import gdata.calendar.service
import datetime
import atom


def acl_sync_cal(cs, cal, initial_role):
	acl_url = 'http://www.google.com/calendar'+ \
				     '/feeds/%s/acl/full' % cal
	feed = cs.GetCalendarAclFeed(acl_url)
	cur = set()
	acc = set()
	for a_rule in feed.entry:
		cur.add(a_rule.scope.value)
	for m in KnUser.objects.all():
		acc.add(m.email.lower())
		if m.email.lower() in cur: continue
		rule = gdata.calendar.CalendarAclEntry()
		rule.scope = gdata.calendar.Scope(value=m.email)
		rule.scope.type = 'user'
		rv = 'http://schemas.google.com/gCal/2005#' + \
				initial_role
		rule.role = gdata.calendar.Role(value=rv)
		print 'Adding %s' % m.email
		cs.InsertAclEntry(rule, acl_url)
	for n in cur - acc:
		print 'WARN Stray %s' % n

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
			  KnUser.objects.all()))
	fn_lut = dict()
	for m in todo:
		fn_lut[m.get_full_name()] = m
	feed = cs.CalendarQuery(query)
	while True:
		for event in feed.entry:
			if not event.title.text in fn_lut:
				print "STRAY EVENT: %s" % event.title.text
				continue
			todo.remove(fn_lut[event.title.text])
		if feed.GetNextLink() is None:
			break
		feed = cs.Query(feed.GetNextLink().href)
	for m in todo:
		if m.dateOfBirth is None:
			continue
		rdata = ('DTSTART;VALUE=DATE:%s\r\n'+
			 'DTEND;VALUE=DATE:%s\r\n'+
			 'RRULE:FREQ=YEARLY\r\n') % (icaldate(m.dateOfBirth),
			icaldate(m.dateOfBirth + datetime.timedelta(1)))
		event = gdata.calendar.CalendarEventEntry()
		event.title = atom.Title(text=m.get_full_name())
		event.content = atom.Content(
			text='Verjaardag van %s'%m.get_full_name())
		event.recurrence = gdata.calendar.Recurrence(text=rdata)
		cs.InsertEvent(event, cal_uri)
		print 'Added %s' % m.get_full_name()

def get_cs():
	username, password = read_ssv_file('gaccount.login')
	cs = gdata.calendar.service.CalendarService()
	cs.email = username
	cs.password = password
	cs.source = 'karpenoktem.nl_sync-1'
	cs.ProgrammaticLogin()
	return cs

if __name__ == '__main__':
	cs = get_cs()
	acl_sync_cal(cs, GCAL_BD, 'read')
	acl_sync_cal(cs, GCAL_UIT, 'editor')
	sync_bd(cs, GCAL_BD)

