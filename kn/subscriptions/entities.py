import decimal

from django.db.models import permalink
from django.utils.html import escape, linebreaks
from django.core.mail import EmailMessage

from kn.leden.mongo import db, SONWrapper, _id, son_property, ObjectId
import kn.leden.entities as Es

ecol = db['events']
scol = db['event_subscriptions']

def ensure_indices():
    ecol.ensure_index('name', unique=True)
    ecol.ensure_index('owner')
    ecol.ensure_index('date')
    scol.ensure_index('user')
    scol.ensure_index('date')
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
    @property
    def createdBy(self):
        return Es.by_id(self._data['createdBy'])

    def get_subscriptions(self):
        for s in scol.find({ 'event': self._data['_id']}).sort('date'):
            yield Subscription(s)
    def get_subscription_of(self, user):
        d = scol.find_one({
            'event': self._data['_id'],
            'user': _id(user)})
        if d is None:
            return None
        return Subscription(d)
    @property
    def description(self):
        return self._data['description']
    @property
    def description_html(self):
        return self._data.get('description_html',
                linebreaks(escape(self._data['description'])))
        # Let wel: 'description' is een *fallback*, het is niet de bedoeling dat
        # deze bij nieuwe actieviteitne nog gebruikt wordt
    @property
    def name(self):
        return self._data['name']
    @property
    def humanName(self):
        return self._data['humanName']
    @property
    def cost(self):
        return decimal.Decimal(self._data['cost'])

    is_open = son_property(('is_open',))
    is_official = son_property(('is_official',), True)
    has_public_subscriptions = son_property(('has_public_subscriptions',),
                                    False)
    mailBody = son_property(('mailBody',))
    subscribedByOtherMailBody = son_property(('subscribedByOtherMailBody',))
    confirmationMailBody = son_property(('confirmationMailBody',))
    everyone_can_subscribe_others = son_property(
            ('everyone_can_subscribe_others',), False)

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
    def date(self):
        return self._data.get('date', None)
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
    def subscribedBy(self):
        if not 'subscribedBy' in self._data:
            return None
        return Es.by_id(self._data['subscribedBy'])
    userNotes = son_property(('userNotes',), None)
    confirmed = son_property(('confirmed',), True)
    subscribedBy_notes = son_property(('subscribedBy_notes',))
    dateConfirmed = son_property(('dateConfirmed',))

    def send_notification(self, subject, body):
        cc = [self.event._data.owner.canonical_full_email]
        if self.subscribedBy:
            cc.append(self.subscribedBy.canonical_full_email)
        email = EmailMessage(
                subject,
                body,
                'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
                [self.user.canonical_full_email],
                cc=cc,
                headers={
                    'Reply-To': self.event._data.owner.canonical_full_email
                },
        )
        email.send()

# vim: et:sta:bs=2:sw=4:
