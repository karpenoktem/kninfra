from kn.leden.mongo import db, SONWrapper, _id, son_property, ObjectId

from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

acol = db['agenda']

def ensure_indices():
    acol.ensure_index('start')

def all(limit=None):
    cursor = acol.find().sort('start')
    if limit is not None:
        cursor = cursor.limit(limit)
    for m in cursor:
        yield AgendaEvent(m)

def update(events):
    """ Clear all current agenda events and replace by events, which is
        a list of quadrupels (title, description, start, end).
        See fetch.fetch. """
    acol.remove()
    for title, description, start, end in events:
        AgendaEvent({'title': title,
                     'description': description,
                     'start': start,
                     'end': end}).save()

class AgendaEvent(SONWrapper):
    def __init__(self, data):
        super(AgendaEvent, self).__init__(data, acol)
    @property
    def id(self):
        return str(self._data['_id'])

    start = son_property(('start',))
    end = son_property(('end',))
    description = son_property(('description',))
    title = son_property(('title',))

    @property
    def description(self):
        text = self._data.get('description', '')
        text = text.replace('Villa van Schaeck',
                    '<a href="{}">Villa van Schaeck</a>'.format(
                                                    reverse('route')))
        return text

    @property
    def month(self):
        return self.start.date().strftime('%B')

    @property
    def shortdate(self):
        return self.start.date().strftime('%a %d')

    @property
    def date(self):
        if self.start.day == self.end.day:
            return self.start.date().strftime('%A %e %B')
        if self.start.month == self.end.month:
            return mark_safe("{} &mdash; {}".format(
                    self.start.date().strftime('%a %e'),
                    self.end.date().strftime('%a %e %B')))
        return mark_safe("{} &mdash; {}".format(
                self.start.date().strftime('%a %e %b'),
                self.end.date().strftime('%a %e %b')))

    def __unicode__(self):
        return self.title

# vim: et:sta:bs=2:sw=4:
