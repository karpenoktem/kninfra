import datetime

from kn.leden.date import now
from kn.leden.mongo import  db, SONWrapper, son_property, _id
import kn.leden.entities as Es

from pymongo import DESCENDING

wcol = db['planning_workers']
pcol = db['planning_pools']
ecol = db['planning_events']
vcol = db['planning_vacancies']

# TODO save vacancies in events?

# ---
def ensure_indices():
    wcol.ensure_index('user')
    wcol.ensure_index('pools')
    vcol.ensure_index('pool')
    vcol.ensure_index('begin')
    vcol.ensure_index('event')
    vcol.ensure_index([('reminder_needed',1), ('event',1)])
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
    def username(self):
        return str(self.user.name)

    def last_shift_in(self, pool):
        self.last_shift = None
        for v in vcol.find({'assignee': _id(self), 'pool': _id(pool)},
                sort=[('begin', DESCENDING)], limit=1):
            return Vacancy(v).begin.date()

    # last_shift is used in a template
    def set_last_shift(self, pool):
        self.last_shift = self.last_shift_in(pool)


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
    kind = son_property(('kind',))

    @classmethod
    def all(cls):
        for c in ecol.find():
            yield cls.from_data(c)

    @classmethod
    def all_in_future(cls):
        return cls.all_since_datetime(now())

    @classmethod
    def all_since_datetime(cls, since):
        for c in ecol.find({'date': {'$gte': since}}):
            yield cls.from_data(c)

    @classmethod
    def by_id(cls, id):
        return cls.from_data(ecol.find_one({'_id': _id(id)}))

    def vacancies(self, pool=None):
        return Vacancy.all_by_event(self, pool)

class Pool(SONWrapper):
    def __init__(self, data):
        super(Pool, self).__init__(data, pcol)
        self._group = None

    @classmethod
    def from_data(cls, data):
        if data is None:
            return None
        return cls(data)

    name = son_property(('name',))
    administrator = son_property(('administrator',))
    reminder_format = son_property(('reminder_format',))
    reminder_cc = son_property(('reminder_cc',))

    @classmethod
    def all(cls):
        for c in pcol.find():
            yield cls.from_data(c)
    @classmethod
    def by_name(cls, n):
        return cls.from_data(pcol.find_one({'name': n}))
    @classmethod
    def by_id(cls, id):
        return cls.from_data(pcol.find_one({'_id': _id(id)}))

    def vacancies(self):
        return Vacancy.all_in_pool(self)

    @property
    def group(self):
        if not self._group:
            self._group = Es.by_name(self.name)
        return self._group

# Generic functions for Vacancy.begin and end.
#
# These fields are either a datetime d or a tuple (d,a),
# where d is a datetime and l is a bool which indicated whether
# d is an approximation.
#
# adt stands for Approximate DateTime.
def adt_to_datetime(r):
    if isinstance(r,datetime.datetime):
        return r
    return r[0]

def adt_is_approximation(r):
    if isinstance(r,datetime.datetime):
        return False
    return r[1]

class Vacancy(SONWrapper):
    formField = None

    name = son_property(('name',))
    event_id = son_property(('event',))
    begin_raw = son_property(('begin',))
    end_raw = son_property(('end',))
    pool_id = son_property(('pool',))
    assignee_id = son_property(('assignee',))
    reminder_needed = son_property(('reminder_needed',))
 
    @property
    def begin(self):
        return adt_to_datetime(self.begin_raw)

    @property
    def begin_is_approximate(self):
        return adt_is_approximation(self.begin_raw)

    @property
    def end(self):
        return adt_to_datetime(self.end_raw)

    @property
    def end_is_approximate(self):
        return adt_is_approximation(self.end_raw)

    def __init__(self, data):
        super(Vacancy, self).__init__(data, vcol)

    @classmethod
    def from_data(cls, data):
        if data is None:
            return None
        return cls(data)

    def get_event(self):
        return Event.by_id(self.event_id)
    def set_event(self, x):
        self.event_id = _id(x)
    event = property(get_event, set_event)

    def get_pool(self):
        return Pool.by_id(self.pool_id)
    def set_pool(self, x):
        self.pool_id = _id(x)
    pool = property(get_pool, set_pool)

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
        return ("~" if self.begin_is_approximate else "") \
                + self.begin.strftime('%H:%M')

    @property
    def end_time(self):
        return ("~" if self.end_is_approximate else "") \
                + self.end.strftime('%H:%M')

    @property
    def id(self):
        return self._id

    @classmethod
    def by_id(cls, id):
        return cls.from_data(vcol.find_one({'_id':  _id(id)}))

    @classmethod
    def all(cls):
        for v in vcol.find():
            yield cls.from_data(v)

    @classmethod
    def all_in_pool(cls, p):
        for v in vcol.find({'pool': _id(p)}):
            yield cls.from_data(v)

    @classmethod
    def all_by_event(cls, e, pool=None):
        f = {'event': _id(e)}
        if pool is not None:
            f['pool'] = _id(pool)
        for v in vcol.find(f):
            yield cls.from_data(v)

    @classmethod
    def all_needing_reminder(cls):
        dt = now() + datetime.timedelta(days=7)
        events = map(lambda e: e['_id'], ecol.find({'date': {'$lte': dt}}))
        for v in vcol.find({'reminder_needed': True, 'event': {'$in': events}}):
            yield cls.from_data(v)

# vim: et:sta:bs=2:sw=4:
