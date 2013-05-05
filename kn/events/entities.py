import decimal

from django.db.models import permalink

from kn.leden.mongo import db, SONWrapper, _id, son_property, ObjectId
import kn.leden.entities as Es

ecol = db['events2'] # TODO change to events

def all_events():
    for d in ecol.find():
        yield Event(d)

def ensure_indices():
    ecol.ensure_index('name', unique=True)
    ecol.ensure_index('when')

def event_by_name(name):
    tmp = ecol.find_one({'name': name})
    return None if tmp is None else Event(tmp)

def event_by_id(__id):
    tmp = ecol.find_one({'_id': _id(__id)})
    return None if tmp is None else Event(tmp)

STATE_SUBSCRIBED        = 0
STATE_NOT_SUBSCRIBED    = 1
STATE_UNCONFIRMED       = 2
STATE_RESERVIST         = 3

class Subscription(SONWrapper):
    def __init__(self, data, event):
        super(Subscription, self).__init__(data, ecol, event)

    # Basic properties
    who = son_property(('who',))
    state = son_property(('state',))
    when = son_property(('when',)) # reference date

    def _get_debit(self):
        return decimal.Decimal(self._data['debit'])
    def _set_debit(self, v):
        self._data['debit'] = str(v)
    debit = property(_get_debit, _set_debit)

    @property
    def changes(self):
        return self._data['changes']


class Event(SONWrapper):
    def __init__(self, data):
        super(Event, self).__init__(data, ecol)

    @property
    def id(self):
        return str(self._data['_id'])

    # Basic properties
    name = son_property(('name',))
    humanName = son_property(('humanName',))
    when = son_property(('when',))
    owner = son_property(('owner',))
    description = son_property(('description',))
    description_html = son_property(('description_html',))
    manually_closed = son_property(('manually_closed',))

    @property
    def cost(self):
        return decimal.Decimal(self._data['cost'])
    
    # Behavioral settings
    has_public_subscriptions = son_property(('has_public_subscriptions',))
    owner_can_subscribe_others = son_property(('owner_can_subscribe_others',))
    anyone_can_subscribe_others = son_property(('anyone_can_subscribe_others',))

    # Part of the contents of the e-mail message sent when someone subscribed
    msg_subscribed = son_property(('msg_subscribed',))
    msg_subscribedBy = son_property(('msg_subscribedBy',))
    msg_confirmed = son_property(('msg_confirmed',))

    def __unicode__(self):
        return unicode('%s (%s)' % (self.humanName, self.owner))

    @permalink
    def get_absolute_url(self):
        return ('event-detail', (), {'name': self.name})

    def has_read_access(self, user):
        return  (self.owner == user or
            str(self.owner.name) in user.cached_groups_names or
               'secretariaat' in user.cached_groups_names or
               'admlezers' in user.cached_groups_names)

    def has_write_access(self, user):
        return (self.owner == user or
            str(self.owner.name) in user.cached_groups_names or
               'secretariaat' in user.cached_groups_names)

    def has_debit_access(self, user):
        return ('penningmeester' in user.cached_groups_names or
                'secretariaat' in user.cached_groups_names)

    @property
    def changes(self):
        return self._data['changes']

    @property
    def subscriptions(self):
        return [Subscription(d, self) for d in  self._data['subscriptions']]

    @property
    def is_open(self):
        return not self.manually_closed


# vim: et:sta:bs=2:sw=4:
