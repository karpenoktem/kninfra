from django.db.models import permalink

from kn.leden.mongo import db, SONWrapper, _id, son_property
import kn.leden.entities as Es

# Polls:
# {'name': 'examplePoll',
#  'humanName': 'Example Poll',
#  'description': 'This is an example poll',
#  'questions': [['My favorite color', ['Red', 'Green', 'White']],
#                ['I like strawberries', ['Yes', 'No']]],
#  'date': datetime(2011, 11, 11, 11, 11),
#  'is_open': True}
pcol = db['polls']

# Fillings:
# {'poll': ObjectID(...),       # of the poll
#  'user': ObjectID(...),       # of the user
#  'answers': [1,0],            # Green and Yes
#  'date': datetime(2011, 11, 12, 12, 12)}
fcol = db['polls_filling']


def ensure_indices():
    # For Poll, we want (1) fast queries on the name
    pcol.ensure_index('name', unique=True)
    #  and (2) fast sorting on date
    pcol.ensure_index('date')
    # For Fillings, we want (I)
    #  This compound index, which will allow fast queries for (1) poll and
    #  user at the same time and on (2) poll.
    fcol.ensure_index([('poll', 1), ('user', 1)])
    #  But we also want fast queries on (II) the user.
    fcol.ensure_index('user')

# Query functions
# ######################################################################


def all_polls():
    for m in pcol.find().sort('date'):
        yield Poll(m)


def poll_by_name(name):
    tmp = pcol.find_one({'name': name})
    return None if tmp is None else Poll(tmp)


def poll_by_id(__id):
    tmp =  pcol.find_one({'_id': _id(__id)})
    return None if tmp is None else Poll(tmp)


def filling_by_user_and_poll(user, poll):
    tmp = fcol.find_one({'poll': _id(poll),
                         'user': _id(user)})
    return None if tmp is None else Filling(tmp)


def filling_by_poll(poll):
    for tmp in fcol.find({'poll': _id(poll)}):
        yield Filling(tmp)

# Models
# ######################################################################


class Poll(SONWrapper):
    def __init__(self, data):
        super(Poll, self).__init__(data, pcol)

    @property
    def id(self):
        return str(self._data['_id'])

    @property
    def createdBy(self):
        return Es.by_id(self._data['createdBy'])

    description = son_property(('description',))
    name = son_property(('name',))
    humanName = son_property(('humanName',))
    is_open = son_property(('is_open',))
    date = son_property(('date',))
    questions = son_property(('questions',))

    def filling_for(self, user):
        return filling_by_user_and_poll(user, self)

    def fillings(self):
        return filling_by_poll(self)

    def __unicode__(self):
        return self.humanName

    @permalink
    def get_absolute_url(self):
        return ('poll', (), {'name': self.name})


class Filling(SONWrapper):
    def __init__(self, data):
        super(Filling, self).__init__(data, fcol)

    @property
    def id(self):
        return str(self._data['_id'])

    @property
    def poll(self):
        return Event(poll_by_id(self._data['poll']))

    @property
    def user(self):
        return Es.by_id(self._data['user'])

    answers = son_property(('answers',))
    date = son_property(('date',))

    def __unicode__(self):
        return unicode(u"answers of %s for %s" % (
                self.user.humanName, self.poll.humanName))

# vim: et:sta:bs=2:sw=4:
