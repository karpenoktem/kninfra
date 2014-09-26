from datetime import datetime
from iso8601 import parse_date

import gdata
import gdata.calendar
import gdata.calendar.service

DEFAULT_CID = 'vssp95jliss0lpr768ec9spbd8@group.calendar.google.com'

def parse_date_range(start, end):
    """ Ugly hack to properly parse gdata date ranges """
    hack_on_end = False
    if start.find('T') == -1:
        start += 'T00:00:00.000'
    if end.find('T') == -1:
        end += 'T23:59:59.000'
        hack_on_end = True
    if hack_on_end:
        the_end_date = parse_date(end) - timedelta(1,0,0)
    else:
        the_end_date = parse_date(end)
    return (parse_date(start),
            the_end_date )

def fetch(cid=None):
    # TODO move to settings.py
    if cid is None:
        cid = DEFAULT_CID
    r = []
    now = datetime.now()
    cs = gdata.calendar.service.CalendarService()
    q = gdata.calendar.service.CalendarEventQuery(cid, 'public', 'full')
    q.start_min = "%s-%s-%s" % (now.year,
                                str(now.month).zfill(2),
                                str(now.day).zfill(2))
    feed = cs.CalendarQuery(q)
    for i, an_event in enumerate(feed.entry):
        if not an_event.when:
            continue
        r.append((an_event.title.text,
                  an_event.content.text,)+
                  parse_date_range(an_event.when[0].start_time,
                  an_event.when[0].end_time))
    return r

if __name__ == '__main__':
    from kn.agenda.entities import update
    update(fetch())

# vim: et:sta:bs=2:sw=4:
