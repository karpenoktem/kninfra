import decimal
import datetime

from django.db.models import permalink
from django.utils.html import escape, linebreaks
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.conf import settings

from kn.leden.mongo import db, SONWrapper, _id, son_property
import kn.leden.entities as Es

ecol = db['events']

# Example of an event
# ------------------
# { "_id" : ObjectId("55631d03ed25c3345751714a"),
#   "name" : "loco-activiteit",
#   "humanName" : "Activiteit van de LoCo",
#   "date" : ISODate("2015-05-25T00:00:00Z"),
#   "cost" : "3",
#   "is_open" : true,
#   "createdBy" : ObjectId("50f29894d4080076aa541de2"),
#   "owner" : ObjectId("4e6fcc85e60edf3dc000006f"),
#   "is_official" : false,
#   "description" : "Beschrijving (in **Markdown**).",
#   "description_html" : "<p>Beschrijving (in <strong>Markdown</strong>).</p>",
#   "everyone_can_subscribe_others" : true,
#   "has_public_subscriptions" : true,
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
#         "inviteDate" : ISODate("2015-06-10T19:37:32.514Z") } ],
#   "mailBody" : "Hallo %(firstName)s,\r\n\r\nJe hebt je aangemeld voor %(eventName)s.\r\n\r\nJe opmerkingen waren:\r\n%(notes)s\r\n\r\nMet een vriendelijke groet,\r\n\r\n%(owner)s",
#   "confirmationMailBody" : "Hallo %(firstName)s,\r\n\r\nJe hebt je aanmelding voor %(eventName)s bevestigd.\r\n\r\nMet een vriendelijke groet,\r\n\r\n%(owner)s",
#   "subscribedByOtherMailBody" : "Hallo %(firstName)s,\r\n\r\nJe bent door %(by_firstName)s aangemeld voor %(eventName)s.\r\n\r\n%(by_firstName)s opmerkingen waren:\r\n%(by_notes)s\r\n\r\nOm deze aanmelding te bevestigen, bezoek:\r\n  %(confirmationLink)s\r\n\r\nMet een vriendelijke groet,\r\n\r\n%(owner)s"
# }
#
# Possible states:
#   * "subscribed"
#   * "unsubscribed" (unimplemented)
#   * "reserve"      (unimplemented)
# When someone has a subscription but no history that person is only invited,
# not subscribed.
#
# Cost: decimal string how much participating in the event will cost.

class SubscriptionError(Exception):
    pass

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

class Event(SONWrapper):
    def __init__(self, data):
        super(Event, self).__init__(data, ecol)
        self._subscriptions = {str(d['user']): Subscription(d, self)
                               for d in data.get('subscriptions', [])}
    name = son_property(('name',))
    humanName = son_property(('humanName',))
    date = son_property(('date',))
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
    def subscriptions(self):
        return [s for s in self._subscriptions.values() if s.subscribed]
    @property
    def invitations(self):
        return filter(lambda s: s.invited and not s.state,
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

    def subscribe(self, user, notes):
        subscription = self.get_subscription(user, create=True)
        subscription.subscribe(notes)
        return subscription
    def invite(self, user, notes, inviter):
        subscription = self.get_subscription(user, create=True)
        subscription.invite(inviter, notes)
        return subscription

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
    def state(self):
        return self.lastMutation.get('state')
    @property
    def subscribed(self):
        return self.state == 'subscribed'
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
        if self.subscribed:
            raise SubscriptionError('User already subscribed')
        self.push_mutation({
            'state': 'subscribed',
            'notes': notes,
            'date': datetime.datetime.now()})
        self.save()
        self.send_notification(
                "Aanmelding %s" % self.event.humanName,
                 self.event.mailBody % {
                    'firstName': self.user.first_name,
                    'eventName': self.event.humanName,
                    'owner': self.event.owner.humanName,
                    'notes': notes})
    def invite(self, inviter, notes):
        if self.invited or self.state:
            raise SubscriptionError('Cannot invite user')
        self._data['inviter'] = _id(inviter)
        self._data['inviteDate'] = datetime.datetime.now()
        self._data['inviterNotes'] = notes
        self.save()
        self.send_notification(
                "Uitnodiging " + self.event.humanName,
                 self.event.subscribedByOtherMailBody % {
                    'firstName': self.user.first_name,
                    'by_firstName': inviter.first_name,
                    'by_notes': notes,
                    'eventName': self.event.humanName,
                    'confirmationLink': (settings.BASE_URL +
                            reverse('event-detail', args=(self.event.name,))),
                    'owner': self.event.owner.humanName})

    def send_notification(self, subject, body):
        cc = [self.event.owner.canonical_full_email]
        if self.invited:
            cc.append(self.inviter.canonical_full_email)
        # See RFC5322 for a description of the References and In-Reply-To
        # headers:
        # https://tools.ietf.org/html/rfc5322#section-3.6.4
        # They are used here for proper threading in mail applications.
        email = EmailMessage(
                subject,
                body,
                'Karpe Noktem Activiteiten <root@karpenoktem.nl>',
                [self.user.canonical_full_email],
                cc=cc,
                headers={
                    'Reply-To': self.event.owner.canonical_full_email,
                    'In-Reply-To': self.event.messageId,
                    'References': self.event.messageId,
                },
        )
        email.send()

# vim: et:sta:bs=2:sw=4:
