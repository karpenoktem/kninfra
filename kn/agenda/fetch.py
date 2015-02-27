# Temporary replacement of the old Google Data code.  Instead of doing a
# targeted query, we'll simply download all events in ical format.

import datetime

import icalendar  # python-icalendar
import urllib2

import django.utils.timezone

DEFAULT_ICAL = ('https://www.google.com/calendar/ical/'+
                'vssp95jliss0lpr768ec9spbd8'+
                '%40group.calendar.google.com/public/basic.ics')

def normalize_ical_dt(dt):
    if isinstance(dt, datetime.date):
        return datetime.datetime.combine(dt, datetime.datetime.min.time())
    return dt

def fetch():
    f = urllib2.urlopen(DEFAULT_ICAL)
    cal = icalendar.Calendar.from_ical(f.read())
    f.close()
    r = []
    now_tz = django.utils.timezone.now() - datetime.timedelta(1)
    now = datetime.datetime.now() - datetime.timedelta(1)
    for c in cal.walk():
        if not c.name == 'VEVENT':
            continue
        start = normalize_ical_dt(c.get('dtstart').dt)
        end = normalize_ical_dt(c.get('dtend').dt)
        if ((end.tzinfo and end < now_tz) or
                ((not end.tzinfo) and end < now)):
            continue
        r.append((c.get('summary'),
                  c.get('description'),
                  start,
                  end))
    return r

# vim: et:sta:bs=2:sw=4:
