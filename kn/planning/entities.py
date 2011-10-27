# vim: et:sta:bs=2:sw=4:
from kn.leden.mongo import  db, SONWrapper, son_property, _id
import kn.leden.entities as Es
from kn.leden.date import now

import datetime

from pymongo import DESCENDING

wcol = db['planning_workers']
pcol = db['planning_pools']
ecol = db['planning_events']
vcol = db['planning_vacancies']

# TODO save vacancies in events

# ---
def ensure_indices():
    wcol.ensure_index('user')
    wcol.ensure_index('pools')
    vcol.ensure_index('pool')
    vcol.ensure_index('begin')
    vcol.ensure_index('event')
    vcol.ensure_index((('reminder_sent',1), ('event',1)))
    pcol.ensure_index('name')
    ecol.ensure_index('date')


class Worker(SONWrapper):
    def __init__(self, data):
        super(Worker, self).__init__(data, wcol)
    @classmethod
    def from_data(cls, data):
    if data is None:
            return None
        return cls(data)
    pools = son_property(('pools',))
    user_id = son_property(('user',))

    @classmethod
    def all(cls):
        for m in wcol.find():
            yield cls.from_data(m)

    @classmethod
    def all_in_pool(cls, p):
        for m in wcol.find({'pools':  _id(p)}):
            yield cls.from_data(m)

    @classmethod
    def by_id(cls, id):
        return cls.from_data(wcol.find_one({'_id':  _id(id)}))

    @property
    def id(self):
        return self._id

    def get_user(self):
        return Es.by_id(self.user_id)
    def set_user(self, x):
        self.user_id = _id(x)
    user = property(get_user, set_user)

    @property
    def is_active(self):
        return self.is_active_at(now())

    def is_active_at(self, dt):
    # TODO ?!
        return self.get_user().get_related(None, dt, dt, False,
        False, False).count() > 0

    def gather_last_shift(self):
        self.last_shift = None
        for v in vcol.find({'assignee': _id(self)},
        sort=[('begin', DESCENDING)], limit=1):
            self.last_shift = v


class Event(SONWrapper):
    def __init__(self, data):
        super(Event, self).__init__(data, ecol)

    @classmethod
    def from_data(cls, data):
    if data is None:
            return None
        return cls(data)

    name = son_property(('name',))
    date = son_property(('date',))

    @classmethod
    def all(cls):
        for c in ecol.find():
            yield cls.from_data(c)

    @classmethod
    def all_in_future(cls):
        for c in ecol.find({'date':
        {'$gte': now() - datetime.timedelta(days=1)}}):
            yield cls.from_data(c)

    @classmethod
    def by_id(cls, id):
        return cls.from_data(ecol.find_one({'_id': _id(id)}))

    def vacancies(self):
        return Vacancy.all_by_event(self)

class Pool(SONWrapper):
    def __init__(self, data):
        super(Pool, self).__init__(data, pcol)

    @classmethod
    def from_data(cls, data):
    if data is None:
            return None
        return cls(data)

    name = son_property(('name',))
    administrator = son_property(('administrator',))

    @classmethod
    def all(cls):
        for c in pcol.find():
            yield cls.from_data(c)
    @classmethod
    def by_name(cls, n):
        return cls.from_data(pcol.find_one({'name': n}))

    def vacancies(self):
        return Vacancy.all_in_pool(self)

class Vacancy(SONWrapper):
    formField = None

    name = son_property(('name',))
    event_id = son_property(('event',))
    begin = son_property(('begin',))
    end = son_property(('end',))
    pool_id = son_property(('pool',))
    assignee_id = son_property(('assignee',))
    reminder_sent = son_property(('reminder_sent',))

    def __init__(self, data):
        super(Vacancy, self).__init__(data, vcol)
        self.reminder_sent = False

    def get_event(self):
        return Event.by_id(self.event_id)
    def set_event(self, x):
        self.event_id = _id(x)
    event = property(get_event, set_event)

    @classmethod
    def from_data(cls, data):
    if data is None:
            return None
        return cls(data)

    def get_assignee(self):
        aid = self.assignee_id
    if aid is None:
            return None
        return Worker.by_id(self.assignee_id)

    def set_assignee(self, value):
    if value is None:
            self.assignee_id = None
        else:
            self.assignee_id = _id(value)
    assignee = property(get_assignee, set_assignee)

    def set_form_field(self, f):
        self.formField = f

    def get_form_field(self, ):
        return self.formField.__str__()

    @property
    def begin_time(self):
        return self.begin.strftime('%H:%M')

    @property
    def end_time(self):
        return self.end.strftime('%H:%M')

    @classmethod
    def all_in_pool(cls, p):
        for v in vcol.find({'pool': _id(p)}):
            yield cls.from_data(v)

    @classmethod
    def all_by_event(cls, e):
        for v in vcol.find({'event': _id(e)}):
            yield cls.from_data(v)

    @classmethod
    def all_needing_reminder(cls):
        dt = now() + datetime.timedelta(days=7)
        events = list()
        for e in ecol.find({'date': {'$lte': dt}}):
            events.append(e)
        for v in vcol.find({'reminder_sent': False,
            'event': {'$in': events}}):
            yield cls.from_data(v)


#def by_name(name):
#   d = mcol.find_one({'list': name})
#   return None if d is None else ModerationRecord(d)