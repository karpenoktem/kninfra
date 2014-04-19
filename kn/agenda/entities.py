from kn.leden.mongo import db, SONWrapper, _id, son_property, ObjectId

acol = db['agenda']

def ensure_indices():
    acol.ensure_index('when')

def all():
    for m in acol.find():
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
    def month(self):
        return self.start.date().strftime('%B')

    def __unicode__(self):
        return self.title

# vim: et:sta:bs=2:sw=4:
