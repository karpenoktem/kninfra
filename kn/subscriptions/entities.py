import decimal
import datetime

from django.db.models import permalink
from django.utils.html import escape, linebreaks
from django.core.urlresolvers import reverse
from django.conf import settings

from kn.base.mail import render_then_email
from kn.leden.mongo import db, SONWrapper, _id, son_property
import kn.leden.entities as Es

ecol = db['events']

# Example of an event
# ------------------
# { "_id" : ObjectId("55631d03ed25c3345751714a"),
#   "_version" : 1,
#   "name" : "loco-activiteit",
#   "humanName" : "Activiteit van de LoCo",
#   "date" : ISODate("2015-05-25T00:00:00Z"),
#   "cost" : "3.40",
#   "max_subscriptions": 24,
#   "is_open" : true,
#   "createdBy" : ObjectId("50f29894d4080076aa541de2"),
#   "owner" : ObjectId("4e6fcc85e60edf3dc000006f"),
#   "is_official" : false,
#   "description" : "Beschrijving (in **Markdown**).",
#   "description_html" : "<p>Beschrijving (in <strong>Markdown</strong>).</p>",
#   "has_public_subscriptions" : true,
#   "may_unsubscribe": true,
#   "subscriptions" : [
#       { "user" : ObjectId("4e6fcc85e60edf3dc0000b9f"),
#         "inviter" : ObjectId("50f29894d4080076aa541de2"),
#         "inviterNotes" : "foo",
#         "inviteDate" : ISODate("2015-06-10T19:36:50.352Z"),
#         "history" : [ { "date" : ISODate("2015-06-10T19:37:01.992Z"),
#                         "state" : "subscribed",
#                         "notes" : "bar" } ] },
#       { "user" : ObjectId("50f29894d4080076aa541de2"),
#         "history" : [ { "date" : ISODate("2015-06-10T19:37:24.555Z"),
#                         "state" : "subscribed",
#                         "notes" : "" } ] },
#       { "user" : ObjectId("4e6fcc85e60edf3dc00001d4"),
#         "inviter" : ObjectId("50f29894d4080076aa541de2"),
#         "inviterNotes" : "",
#         "inviteDate" : ISODate("2015-06-10T19:37:32.514Z") } ]
# }
#
# Possible states:
#   * "subscribed"
#   * "unsubscribed"
#   * "reserve"      (unimplemented)
# When someone has a subscription but no history that person is only invited,
# not subscribed.

def ensure_indices():
    ecol.ensure_index('name', unique=True)
    ecol.ensure_index('owner')
    ecol.ensure_index('date')

def all_events():
    for m in ecol.find().sort('date'):
        yield Event(m)

def event_by_name(name):
    tmp = ecol.find_one({'name': name})
    return None if tmp is None else Event(tmp)
def event_by_id(__id):
    tmp = ecol.find_one({'_id': _id(__id)})
    return None if tmp is None else Event(tmp)

def is_superuser(user):
    return 'secretariaat' in user.cached_groups_names

def may_set_owner(user, owner):
    if is_superuser(owner):
        return True
    comms = Es.id_by_name('comms', use_cache=True)
    allowTag = Es.id_by_name('!can-organize-official-events', use_cache=True)
    return owner.has_tag(comms) or owner.has_tag(allowTag)


class Event(SONWrapper):
    def __init__(self, data):
        super(Event, self).__init__(data, ecol, detect_race=True)
        self._subscriptions = {str(d['user']): Subscription(d, self)
                               for d in data.get('subscriptions', [])}
    name = son_property(('name',))
    humanName = son_property(('humanName',))
    date = son_property(('date',))
    may_unsubscribe = son_property(('may_unsubscribe',))
    @property
    def id(self):
        return str(self._data['_id'])
    @property
    def owner(self):
        return Es.by_id(self._data['owner'])
    @property
    def createdBy(self):
        return Es.by_id(self._data['createdBy'])
    @property
    def listSubscribed(self):
        return [s for s in self._subscriptions.values() if s.subscribed]
    @property
    def listUnsubscribed(self):
        return [s for s in self._subscriptions.values() if s.unsubscribed]
    @property
    def listInvited(self):
        return filter(lambda s: s.invited and not s.has_mutations,
                      self._subscriptions.values())
    def get_subscription(self, user, create=False):
        '''
        Return Subscription for user, creating it if it doesn't already exist.
        '''
        subscription = self._subscriptions.get(str(_id(user)))
        if subscription or not create:
            return subscription
        if 'subscriptions' not in self._data:
            self._data['subscriptions'] = []
        d = {'user': _id(user)}
        self._data['subscriptions'].append(d)
        subscription = Subscription(d, self)
        self._subscriptions[str(_id(user))] = subscription
        return subscription
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
    def cost(self):
        return decimal.Decimal(self._data['cost'])

    max_subscriptions = son_property(('max_subscriptions',))
    is_open = son_property(('is_open',))
    is_official = son_property(('is_official',), True)
    has_public_subscriptions = son_property(('has_public_subscriptions',),
                                    False)

    def __unicode__(self):
        return unicode('%s (%s)' % (self.humanName, self.owner))

    @property
    def history(self):
        return [HistoryEvent(d, self) for d in self._data.get('history', [])]

    @permalink
    def get_absolute_url(self):
        return ('event-detail', (), {'name': self.name})
    @property
    def messageId(self):
        """ Unique ID to be used in e.g. References: headers """
        return '<%s@%s>' % (self.get_absolute_url().strip('/'),
                        settings.MAILDOMAIN)
    def has_read_access(self, user):
        return  self.owner == user or \
            str(self.owner.name) in user.cached_groups_names or \
               'secretariaat' in user.cached_groups_names or \
               'admlezers' in user.cached_groups_names
    def has_write_access(self, user):
        return self.owner == user or \
            str(self.owner.name) in user.cached_groups_names or \
               'secretariaat' in user.cached_groups_names
    @property
    def can_subscribe(self):
        if self.max_subscriptions is not None and \
                len(self.listSubscribed) >= self.max_subscriptions:
            return False
        return self.is_open
    @property
    def can_unsubscribe(self):
        return self.is_open and self.may_unsubscribe
    @property
    def is_member_activity(self):
        if self.is_official:
            return False
        return self.owner.id == self.createdBy.id

    def subscribe(self, user, notes):
        subscription = self.get_subscription(user, create=True)
        subscription.subscribe(notes)
        return subscription
    def unsubscribe(self, user, notes):
        subscription = self.get_subscription(user, create=True)
        subscription.unsubscribe(notes)
        return subscription
    def invite(self, user, notes, inviter):
        subscription = self.get_subscription(user, create=True)
        subscription.invite(inviter, notes)
        return subscription

    def pushHistory(self, historyEvent):
        if not 'history' in self._data:
            self._data['history'] = []
        self._data['history'].append(historyEvent)
    def open(self, user, save=True):
        if self.is_open:
            return
        self.is_open = True
        self.pushHistory({
            'action': 'opened',
            'date': datetime.datetime.now(),
            'by': _id(user)})
        if save:
            self.save()
    def close(self, user, save=True):
        if not self.is_open:
            return
        self.is_open = False
        self.pushHistory({
            'action': 'closed',
            'date': datetime.datetime.now(),
            'by': _id(user)})
        if save:
            self.save()
    def update(self, data, user, save=True):
        self._data.update(data)
        self.pushHistory({
            'action': 'edited',
            'date': datetime.datetime.now(),
            'by': _id(user)})
        if save:
            self.save()

# Edit events in the event: 'opened', 'closed', 'edited'.
class HistoryEvent(SONWrapper):
    def __init__(self, data, event):
        super(HistoryEvent, self).__init__(data, ecol, event)
        self.event = event

    action = son_property(('action',))
    date = son_property(('date',))

    @property
    def user(self):
        return Es.by_id(self._data['by'])


# A Subscription is the relation between a user and an event. When anything
# happens between the user and the event (invitation, subscription,
# unsubscription) a Subscription is created or updated. That means a
# subscription can also be 'unsubscribed' (see _state).
# You could also call this an RSVP.
class Subscription(SONWrapper):
    def __init__(self, data, event):
        super(Subscription, self).__init__(data, ecol, event)
        self.event = event

    inviterNotes = son_property(('inviterNotes',))
    inviteDate = son_property(('inviteDate',))
    date = son_property(('date',))
    history = son_property(('history',),)

    def __unicode__(self):
        return unicode(u"<Subscription(%s for %s)>" % (self.user.humanName,
                        self.event.humanName))

    @property
    def id(self):
        return str(self._data['_id'])
    @property
    def user(self):
        return Es.by_id(self._data['user'])
    @property
    def invited(self):
        return 'inviter' in self._data
    @property
    def inviter(self):
        return Es.by_id(self._data.get('inviter'))
    @property
    def lastMutation(self):
        if not self.history:
            return {}
        return self.history[-1]
    def push_mutation(self, mutation):
        if not self.history:
            self.history = []
        self.history.append(mutation)
    @property
    def _state(self):
        return self.lastMutation.get('state')
    @property
    def has_mutations(self):
        return self._state is not None
    @property
    def subscribed(self):
        return self._state == 'subscribed'
    @property
    def unsubscribed(self):
        return self._state == 'unsubscribed'
    @property
    def date(self):
        # last change date
        return self.lastMutation.get('date') or self.inviteDate
    @property
    def userNotes(self):
        return self.lastMutation.get('notes')
    @property
    def notes(self):
        return self.userNotes or self.inviterNotes
    @property
    def subscriber(self):
        subscriber = self.lastMutation.get('subscriber')
        if subscriber is not None:
            return Es.by_id(subscriber)
        return self.user

    def subscribe(self, notes):
        assert not self.subscribed
        mutation = {
            'state': 'subscribed',
            'notes': notes,
            'date': datetime.datetime.now()}
        self.push_mutation(mutation)
        self.save()
        self.send_notification(mutation)
    def unsubscribe(self, notes):
        assert self.subscribed
        mutation = {
            'state': 'unsubscribed',
            'notes': notes,
            'date': datetime.datetime.now()}
        self.push_mutation(mutation)
        self.save()
        self.send_notification(mutation)
    def invite(self, inviter, notes):
        assert not self.invited and not self.has_mutations
        self._data['inviter'] = _id(inviter)
        self._data['inviteDate'] = datetime.datetime.now()
        self._data['inviterNotes'] = notes
        self.save()
        self.send_notification({'state': 'invited'})

    def send_notification(self, mutation,
            template='subscriptions/subscription-notification.mail.html'):
        cc = [self.event.owner.canonical_full_email]
        if self.invited:
            cc.append(self.inviter.canonical_full_email)
        # See RFC5322 for a description of the References and In-Reply-To
        # headers:
        # https://tools.ietf.org/html/rfc5322#section-3.6.4
        # They are used here for proper threading in mail applications.
        render_then_email(template,
                self.user.canonical_full_email,
                ctx={
                    'mutation': mutation,
                    'subscription': self,
                    'event': self.event,
                },
                cc=cc,
                reply_to=self.event.owner.canonical_full_email,
                headers={
                    'In-Reply-To': self.event.messageId,
                    'References': self.event.messageId,
                })

# vim: et:sta:bs=2:sw=4:
