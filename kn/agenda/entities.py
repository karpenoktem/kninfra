import re
from datetime import datetime

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import six
from django.utils.safestring import mark_safe
from django.utils.six.moves import range
from django.utils.translation import get_language

from kn.leden.mongo import SONWrapper, db, son_property

acol = db['agenda']


def ensure_indices():
    acol.ensure_index([('agenda', 1),
                       ('start', 1)])


def events(agenda=None, limit=None):
    query = {'end': {'$gte': datetime.now()}}
    if agenda is not None:
        query['agenda'] = agenda
    cursor = acol.find(query).sort('start')
    if limit is not None:
        cursor = cursor.limit(limit)
    for m in cursor:
        yield AgendaEvent(m)


def update(agendas):
    """ Clear all current agenda events and replace by `agendas', which is a
        dictionary with agendas, where each agenda contains a list of events:
        quadrupels (title, description, start, end). See fetch.fetch. """
    acol.remove()
    for key, events in agendas.items():
        for title, description, start, end, location in events:
            AgendaEvent({'agenda': key,
                         'title': title,
                         'description': description,
                         'start': start,
                         'end': end,
                         'location': location}).save()


@six.python_2_unicode_compatible
class AgendaEvent(SONWrapper):

    def __init__(self, data):
        super(AgendaEvent, self).__init__(data, acol)

    @property
    def id(self):
        return str(self._data['_id'])

    start = son_property(('start',))
    end = son_property(('end',))
    location = son_property(('location',))
    description = son_property(('description',))
    title = son_property(('title',))

    @property
    def description(self):
        lan = six.text_type(get_language()).lower()
        lut = self._parse_description()
        defaultLan = six.text_type(settings.LANGUAGE_CODE).lower()
        return lut.get(lan, lut[defaultLan])

    def _parse_description(self):
        text = self._data.get('description', '')
        # First add auto-links
        text = text.replace('Villa van Schaeck',
                            '<a href="%s">Villa van Schaeck</a>' %
                            reverse('route'))
        # Split on language tags, i.e. [nl], [en], [de]
        # e.g. "Dit is een agendastuk \n[en] This is an agendapiece"
        # becomes ('Dit is een agendastuk', 'en', 'This is an agendapiece')
        splitRegex = '(?:^|\n\\W*)\\[([a-zA-Z-]+)\\](?:\\W*\\n|$)'
        defaultLan = six.text_type(settings.LANGUAGE_CODE).lower()
        bits = [defaultLan] + re.split(splitRegex, text)
        descLut = {}
        for i in range(0, len(bits), 2):
            code = bits[i]
            text = bits[i + 1]
            if code not in descLut:
                descLut[code] = ""
            else:
                descLut[code] += '\n'
            descLut[code] += text
        return descLut

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

    def __str__(self):
        return self.title

# vim: et:sta:bs=2:sw=4:
