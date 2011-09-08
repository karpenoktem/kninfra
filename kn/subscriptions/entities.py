from django.db.models import permalink
from pymongo.objectid import ObjectId

from kn.leden.mongo import db, SONWrapper

import kn.leden.entities as Es

ecol = db['events']
scol = db['event_subscriptions']

def ensure_indices():
	ecol.ensure_index('name', unique=True)
	ecol.ensure_index('owner')
        scol.ensure_index('user')
        scol.ensure_index('event')

def all_events():
        for m in ecol.find():
                yield Event(m)
def all_subscriptions():
        for m in scol.find():
                yield Subscription(m)

def event_by_name(name):
        return Event(ecol.find_one({'name': name}))
def event_by_id(_id):
        return Event(ecol.find_one({'_id': _id}))
def subscription_by_id(_id):
        return Subscription(scol.find_one({'_id': _id}))

class Event(SONWrapper):
        def __init__(self, data):
                super(Event, self).__init__(data, ecol)
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
        def humanName(self):
                return self._data['humanName']
        @property
        def cost(self):
                return self._data['cost']
        @property
        def is_open(self):
                return self._data['is_open']

	def __unicode__(self):
		return unicode('%s (%s)' % (self.humanName, self.owner))

	@permalink
	def get_absolute_url(self):
		return ('event-detail', (), {'name': self.name})

class Subscription(SONWrapper):
        def __init__(self, data):
                super(Subscription, self).__init__(data, scol)

        @property
        def event(self):
                return Event(event_by_id(self._data['event']))
        @property
        def user(self):
                return Es.by_id(self._data['user'])

	def __unicode__(self):
		return unicode(u"%s for %s" % (self.user.humanName,
						self.event.humanName))
        @property
        def debit(self):
                return self._data['debit']
        @property
        def userNotes(self):
                return self._data['userNotes']
