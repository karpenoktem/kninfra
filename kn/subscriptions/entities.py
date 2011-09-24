import decimal

from django.db.models import permalink
from pymongo.objectid import ObjectId

from kn.leden.mongo import db, SONWrapper, _id, son_property

import kn.leden.entities as Es

ecol = db['events']
scol = db['event_subscriptions']

def ensure_indices():
	ecol.ensure_index('name', unique=True)
	ecol.ensure_index('owner')
	ecol.ensure_index('date')
        scol.ensure_index('user')
        scol.ensure_index('event')

def all_events():
        for m in ecol.find().sort('date'):
                yield Event(m)
def all_subscriptions():
        for m in scol.find():
                yield Subscription(m)

def event_by_name(name):
        tmp = ecol.find_one({'name': name})
        return None if tmp is None else Event(tmp)
def event_by_id(__id):
        tmp = ecol.find_one({'_id': _id(__id)})
        return None if tmp is None else Event(tmp)
def subscription_by_id(__id):
        tmp =  scol.find_one({'_id': _id(__id)})
        return None if tmp is None else Subscription(tmp)

class Event(SONWrapper):
        def __init__(self, data):
                super(Event, self).__init__(data, ecol)
        @property
        def id(self):
                return str(self._data['_id'])
        @property
        def date(self):
                return self._data.get('date', None)
        @property
        def owner(self):
                return Es.by_id(self._data['owner'])

        def get_subscriptions(self):
                for s in scol.find({ 'event': self._data['_id']}):
                        yield Subscription(s)
        def get_subscription_of(self, user):
                d = scol.find_one({
                        'event': self._data['_id'],
                        'user': user._id})
                if d is None:
                        return None
                return Subscription(d)
        @property
        def description(self):
                return self._data['description']
        @property
        def mailBody(self):
                return self._data['mailBody']
        @property
        def name(self):
                return self._data['name']
        @property
        def humanName(self):
                return self._data['humanName']
        @property
        def cost(self):
                return self._data['cost']

        is_open = son_property(('is_open',))

	def __unicode__(self):
		return unicode('%s (%s)' % (self.humanName, self.owner))

	@permalink
	def get_absolute_url(self):
		return ('event-detail', (), {'name': self.name})
        def has_read_access(self, user):
                return  self.owner == user or \
                        str(self.owner.name) in user.cached_groups_names or \
                       'secretariaat' in user.cached_groups_names or \
                       'admlezers' in user.cached_groups_names
        def has_write_access(self, user):
                return self.owner == user or \
                        str(self.owner.name) in user.cached_groups_names or \
                       'secretariaat' in user.cached_groups_names
        def has_debit_access(self, user):
                return 'penningmeester' in user.cached_groups_names or \
                       'secretariaat' in user.cached_groups_names

class Subscription(SONWrapper):
        def __init__(self, data):
                super(Subscription, self).__init__(data, scol)
        @property
        def id(self):
                return str(self._data['_id'])
        @property
        def event(self):
                return Event(event_by_id(self._data['event']))
        @property
        def user(self):
                return Es.by_id(self._data['user'])

	def __unicode__(self):
		return unicode(u"%s for %s" % (self.user.humanName,
						self.event.humanName))
        def get_debit(self):
                return decimal.Decimal(self._data['debit'])
        def set_debit(self, v):
                self._data['debit'] = str(v)
        debit = property(get_debit, set_debit)
        @property
        def userNotes(self):
                return self._data['userNotes']
