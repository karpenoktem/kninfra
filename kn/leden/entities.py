import re
import hashlib
import datetime
import functools
import email.utils

from django.conf import settings
from django.db.models import permalink
from django.utils.translation import ugettext as _
from django.contrib.auth.hashers import check_password, make_password
from django.utils.crypto import constant_time_compare

from kn.leden.date import now
from kn.leden.mongo import db, SONWrapper, _id, son_property
from kn.base._random import pseudo_randstr

from kn.base.conf import from_settings_import
from_settings_import("DT_MIN", "DT_MAX", globals())

# ######################################################################
# The collections
# ######################################################################
ecol = db['entities']   # entities: users, group, tags, studies, ...

# Example of a user
# ----------------------------------------------------------------------
# {"_id" : ObjectId("4e6fcc85e60edf3dc0000270"),
#  "addresses" : [ { "city" : "Nijmegen",
#                    "zip" : "...",
#                    "number" : "...",
#                    "street" : "...",
#                    "from" : ISODate("2004-..."),
#                    "until" : DT_MAX) } ],
#   "types" : [ "user" ],
#   "names" : [ "giedo" ],
#   "humanNames" : [ { "human" : "Giedo Jansen" } ],
#   "person" : { "given" : null,
#                "family" : "Jansen",
#                "nick" : "Giedo",
#                "gender" : "m",
#                "dateOfBirth" : ISODate("..."),
#                "titles" : [ ] },
#   "is_active" : 0,
#   "emailAddresses" : [ { "email" : "...",
#                          "from" : ISODate("2004-08-31T00:00:00Z"),
#                          "until" : DT_MAX } ],
#   "password" : "pbkdf2_sha256$15000$...$...",
#   "studies" : [ { "institute" : ObjectId("4e6fcc85e60edf3dc000001d"),
#                   "study" : ObjectId("4e6fcc85e60edf3dc0000030"),
#                   "number" : "...",
#                   "from" : ...,
#                   "until" : DT_MAX } ],
#   "telephones" : [ { "number" : "...",
#                      "from" : ISODate("2004-08-31T00:00:00Z"),
#                      "until" : ISODate("5004-09-01T00:00:00Z") } ] },
#   "preferences" : {
#       "visibility" : {
#           "telephone" : false
#       }
#   }
# }

# NOTE password can also be of the old-style form
#   "password" : {"hash" : "...","salt" : "...", "algorithm" : "sha1" }

# Example of a tag
# ----------------------------------------------------------------------
# { "_id" : ObjectId("4e6fcc85e60edf3dc0000004"),
#   "types" : [ "tag" ],
#   "names" : [ "!year-group" ],
#   "humanNames" : [ { "name" : "!year-group", "human" : "Jaargroep" } ],
#   "tags" : [ ObjectId("4e6fcc85e60edf3dc0000000") ]
# }

# Example of a study
# ----------------------------------------------------------------------
# { "_id" : ObjectId("4e6fcc85e60edf3dc0000033"),
#   "humanNames" : [ { "human" : "Geschiedenis" } ],
#   "types" : [ "study" ]
# }

# Example of an institute
# ----------------------------------------------------------------------
# { "_id" : ObjectId("4e6fcc85e60edf3dc0000016"),
#   "humanNames" : [ { "human" : "Radboud Universiteit Nijmegen" } ],
#   "types" : [ "institute" ]
# }

# Example of a group
# ----------------------------------------------------------------------
# { "_id" : ObjectId("4e6fcc85e60edf3dc0000067"),
#   "types" : [ "group", "tag" ],
#   "description" : "Het bestuur",
#   "names" : [ "bestuur", "bestuul", "parkhangen", "festivals", "b" ],
#   "humanNames" : [ { "name" : "bestuur",
#                      "human" : "Bestuur",
#                      "genitive_prefix" : "van het" } ],
#   "tags" : [ ObjectId("4e6fcc85e60edf3dc0000004") ]
# }

# Example of a brand
# ----------------------------------------------------------------------
# { "_id" : ObjectId("4e6fcc85e60edf3dc0000bcb"),
#   "types" : [ "brand" ],
#   "tags" : [ ObjectId("4e6fcc85e60edf3dc0000003") ],
#   "humanNames" : [ { "human" : "Vice-voorzitter" } ],
#   "sofa_suffix" : "vicevoorzitter",
#   "names" : [ ]
# }

rcol = db['relations']  # relations: "giedo is chairman of bestuur from
                        #             date A until date B"
# Example of a brand
# ----------------------------------------------------------------------
# This is the relation: "mike is chair (voorzitter) of the soco from
#   2012-02-07 to 2013-03-11, but he should not be put in soco9
#   (which is forced by the year-override tag)". 
# { "_id" : ObjectId("4f3086270032a05bfd000005"),
#   "from" : ISODate("2012-02-07T03:02:15.130Z"),
#   "how" : ObjectId("4e6fcc85e60edf3dc0000bc8"),
#   "tags" : [ ObjectId("5038e25b0032a04438000000") ],
#   "until" : ISODate("2013-03-11T20:16:36.203Z"),
#   "who" : ObjectId("4e6fcc85e60edf3dc0000356"),
#   "with" : ObjectId("4e6fcc85e60edf3dc0000077")
# }

ncol = db['notes']      # notes on entities by the secretaris
# Example of a note
# ----------------------------------------------------------------------
# { "_id" : ObjectId("4e99b5460032a006e3000013"),
#   "on" : ObjectId("4e6fcc85e60edf3dc000029d"),
#   "closed_by" : ObjectId("4e6fcc85e60edf3dc00001d4"),
#   "note" : "Adres veranderd. Was:  (...) Nijmegen",
#   "at" : ISODate("2011-03-24T00:00:00Z"),
#   "closed_at" : ISODate("2012-08-25T14:53:17.413Z"),
#   "open" : false,
#   "by" : ObjectId("4e6fcc85e60edf3dc0000410")
# }

pcol = db['push_changes'] # Changes to be pushed to remote systems
# TODO add example

incol = db['informacie_notifications'] # human readable list of notifications 
                                        #for informacie group
# TODO add example

def get_hexdigest(algorithm, salt, raw_password):
    """ Used to check old-style passwords. """
    assert algorithm == 'sha1'
    return hashlib.sha1(salt + raw_password).hexdigest()

def ensure_indices():
    """ Ensures that the indices we need on the collections are set """
    # entities
    # NOTE On some versions of Mongo, a unique sparse index does not allow
    #      more than one entitity without a name.
    #ecol.ensure_index('names', unique=True, sparse=True)
    ecol.ensure_index('names', sparse=True)
    ecol.ensure_index('types')
    ecol.ensure_index('tags', sparse=True)
    ecol.ensure_index('humanNames.human')
    ecol.ensure_index('studies.study', sparse=True)
    ecol.ensure_index('studies.institute', sparse=True)
    ecol.ensure_index('person.dateOfBirth', sparse=True)
    # relations
    rcol.ensure_index('how', sparse=True)
    rcol.ensure_index('with')
    rcol.ensure_index('who')
    rcol.ensure_index('tags', sparse=True)
    rcol.ensure_index([('until',1),
               ('from',-1)])
    # notes
    ncol.ensure_index([('on', 1),
                       ('at', 1)])
    ncol.ensure_index([('open',1),
                       ('at',1)])
    # informacie notifications
    incol.ensure_index('when')


# Basic functions to work with entities
# ######################################################################

class EntityException(Exception):
    '''
    Exception that is raised when invalid input is entered (e.g. overlapping
    dates).
    '''
    pass

def entity(d):
    """ Given a dictionary, returns an Entity object wrapping it """
    if d is None:
        return None
    return TYPE_MAP[d['types'][0]](d)

def of_type(t):
    """ Returns all entities of type @t """
    for m in ecol.find({'types': t}):
        yield TYPE_MAP[t](m)

def of_type_by_name(t):
    """ Returns a `name -> entity' dictionary for the
        entities of tyoe @t """
    ret = {}
    for m in ecol.find({'types': t}):
        e = entity(m)
        for n in m['names']:
            ret[n] = e
    return ret

groups = functools.partial(of_type, 'group')
users = functools.partial(of_type, 'user')
studies = functools.partial(of_type, 'study')
institutes = functools.partial(of_type, 'institute')
tags = functools.partial(of_type, 'tag')
brands = functools.partial(of_type, 'brand')

def by_ids(ns):
    """ Find entities by a list of _ids """
    ret = {}
    for m in ecol.find({'_id': {'$in': ns}}):
        ret[m['_id']] = entity(m)
    return ret

__id2name_cache = {}

def id_by_name(n, use_cache=False):
    """ Find the _id of entity with name @n """
    ret = None
    if use_cache:
        if n in __id2name_cache:
            ret =  __id2name_cache[n]
    if ret is None:
        obj = ecol.find_one({'names': n}, {'names':1})
        if obj is None:
            return None
        ret = obj['_id']
        if use_cache:
            __id2name_cache[n] = ret
    return ret

def ids_by_names(ns=None, use_cache=False):
    """ Finds _ids of entities by a list of names """
    ret = {}
    nss = None if ns is None else frozenset(ns)
    if use_cache and ns is not None:
        nss2 = set(nss)
        for n in nss:
            if n in __id2name_cache:
                ret[n] = __id2name_cache[n]
                nss2.remove(n)
        nss = frozenset(nss2)
    for m in ecol.find({} if ns is None else
            {'names': {'$in': tuple(nss)}}, {'names':1}):
        for n in m.get('names',()):
            if ns is None or n in nss:
                ret[n] = m['_id']
                if use_cache and ns is not None:
                    __id2name_cache[n] = m['_id']
                continue
    return ret

def by_names(ns):
    """ Finds entities by a list of names """
    ret = {}
    nss = frozenset(ns)
    for m in ecol.find({'names': {'$in': ns}}):
        for n in m['names']:
            if n in nss:
                ret[n] = entity(m)
                continue
    return ret

def by_name(n):
    """ Finds an entity by name """
    return entity(ecol.find_one({'names': n}))

def by_id(n):
    """ Finds an entity by id """
    if n is None: return None
    return entity(ecol.find_one({'_id': _id(n)}))

def by_study(study):
    """ Finds entities by studies.study """
    for m in ecol.find({'studies.study': _id(study)}):
        yield entity(m)

def by_institute(institute):
    """ Finds entities by studies.insitute """
    for m in ecol.find({'studies.institute': _id(institute)}):
        yield entity(m)

def get_years_of_birth():
    """ Returns the years of birth.

        NOTE Currently, simply queries for the minimum and maximum date of
        birth and assumes all in between are used. """
    start = ecol.find_one({'person.dateOfBirth': {'$ne': None}},
                     {'person.dateOfBirth': 1},
                     sort=[('person.dateOfBirth', 1)]
                        )['person']['dateOfBirth'].year
    end = ecol.find_one({'person.dateOfBirth': {'$ne': None}},
                     {'person.dateOfBirth': 1},
                     sort=[('person.dateOfBirth', -1)]
                        )['person']['dateOfBirth'].year
    return xrange(start, end+1)

def by_year_of_birth(year):
    """ Finds entities by year of birth """
    for m in ecol.find({'types': 'user',
                        'person.dateOfBirth': {
                                '$lt': datetime.datetime(year + 1, 1, 1),
                                '$gte': datetime.datetime(year, 1, 1) }}):
        yield entity(m)

def by_age(max_age=None):
    """ Finds entities under a certain age """
    # This function could be extended to allow for a range of ages (e.g. adding
    # a min_age argument)
    date = datetime.date.today()
    date = date.replace(year=date.year-max_age)
    dt = datetime.datetime.combine(date, datetime.time(0, 0, 0, 0))
    for m in ecol.find({'types': 'user',
                        'person.dateOfBirth': {
                                '$gt': dt}}):
        yield entity(m)

def all():
    """ Finds all entities """
    for m in ecol.find():
        yield entity(m)

def names_by_ids(ids=None):
    """ Returns an `_id => primary name' dictionary for entities with
        _id in @ids or all if @ids is None """
    ret = {}
    query = {} if ids is None else {'_id': {'$in': ids}}
    for e in ecol.find(query, {'names': True}):
        if e.get('names'):
            ret[e['_id']] = e['names'][0]
        else:
            ret[e['_id']] = None
    return ret

def ids():
    """ Returns a set of all ids """
    ret = set()
    for e in ecol.find({}, {'_id':True}):
        ret.add(e['_id'])
    return ret

def names():
    """ Returns a set of all names """
    ret = set()
    for e in ecol.find({}, {'names':True}):
        ret.update(e.get('names', ()))
    return ret

# Searching entities by keywords
# ######################################################################
def by_keyword(keyword, limit=20, _type=None):
    """ Searches for entities by a keyword. """
    # TODO The current method does not use indices.  It will search
    #      through every single entity.  At the moment, it is fast enough.
    #      To make it future proof, we should implement a query cache.
    #      See MongoCollection.query in mongo.py of github.com/marietje/maried
    # TODO We might want to match names.names too.
    # TODO We want to filter virtual groups and other uninteresting entities
    # TODO We might want to match multiple keywords out-of-order.
    #           eg.: "gi jan" matches Giedo, but "jan gi" does not.
    # TODO We might want to create an index, for when searching on type too
    regex = '.*%s.*' % '.*'.join([
                re.escape(bit) for bit in keyword.split(' ') if bit])
    query_dict = {'humanNames.human': {
                            '$regex': regex, '$options': 'i'}}
    if _type:
        query_dict['types'] = _type
    cursor = ecol.find(query_dict, limit=(0 if limit is None else limit),
                            sort=[('humanNames.human', 1)])
    return map(entity, cursor)

# Specialized functions to work with entities.
# ######################################################################
def bearers_by_tag_id(tag_id, _as=entity):
    """ Find the bearers of the tag with @tag_id """
    return map(_as, ecol.find({'tags': tag_id}))

def year_to_range(year):
    """ Returns (start_date, end_date) for the given year """
    return (datetime.datetime(2003 + year, 9, 1),
            datetime.datetime(2004 + year, 8, 31))

def date_to_year(dt):
    """ Returns the `verenigingsjaar' at the date """
    year =  dt.year - 2004
    if dt.month >= 9:
        year += 1
    if year < 1:
        year = 1
    return year

# Functions to work with relations
# ######################################################################

def relation_is_active_at(rel, dt):
    """ Returns whether @rel is active at @dt """
    return ((rel['until'] is None or rel['until'] >= dt)
            and (rel['from'] is None or rel['from'] <= dt))

def relation_is_active(rel):
    """ Returns whether @rel is active now """
    return relation_is_active_at(rel, now())

def relation_is_virtual(rel):
    """ Returns whether @rel is "virtual".

        Requires rel['with'] to be deref'd """
    return rel['with'].is_group and rel['with'].as_group().is_virtual

def user_may_end_relation(user, rel):
    """ Returns whether @user may end @rel """
    if relation_is_virtual(rel):
        return False
    if not relation_is_active(rel):
        return False
    if 'secretariaat' in user.cached_groups_names:
        return True
    if _id(rel['who']) == _id(user) and \
            rel['how'] is None and \
            by_id(rel['with']).has_tag(id_by_name('!free-to-join', True)):
        return True
    return False

def end_relation(__id):
    dt = now()
    rcol.update({'_id': _id(__id)}, {'$set': {'until': dt}})

def user_may_begin_relation(user, who, _with, how):
    """ Returns whether @user may begin a @how-relation between @who and @_with
    """
    _with_e = by_id(_with)
    user_e = by_id(user)
    if _with_e.is_group and _with_e.as_group().is_virtual:
        return False
    if 'secretariaat' in user_e.cached_groups_names:
        return True
    if _with_e.has_tag(id_by_name('!free-to-join', True)):
        if _id(user) == _id(who) and how is None:
            return True
    return False

def add_relation(who, _with, how=None, _from=None, until=None):
    if _from is None:
        _from = DT_MIN
    if until is None:
        until = DT_MAX
    return rcol.insert({'who': _id(who),
                     'with': _id(_with),
                     'how': None if how is None else _id(how),
                     'from': _from,
                     'until': until})

def user_may_tag(user, group, tag):
    return 'secretariaat' in user.cached_groups_names

def user_may_untag(user, group, tag):
    return 'secretariaat' in user.cached_groups_names

def disj_query_relations(queries, deref_who=False, deref_with=False,
        deref_how=False):
    """ Find relations matching any one of @queries.
        See @query_relations. """
    if not queries:
        return []
    bits = []
    for query in queries:
        for attr in ('with', 'how', 'who'):
            if attr not in query:
                continue
            elif isinstance(query[attr], (list, tuple)):
                query[attr] = {'$in': map(_id, query[attr])}
            elif query[attr] is not None:
                query[attr] = _id(query[attr])
            else:
                query[attr] = None
        if query.get('from') is None: query['from'] = DT_MIN
        if query.get('until') is None: query['until'] = DT_MAX
        # When DT_MIN < from < until < DT_MAX we need the most complicated
        # query. However, in the following four cases we can simplify the
        # required query bits.
        if query['from'] == DT_MIN and query['until'] == DT_MAX:
            del query['from']
            del query['until']
            bits.append(query)
        elif query['from'] == query['until']:
            query['from'] = {'$lte': query['from']}
            query['until'] = {'$gte': query['until']}
            bits.append(query)
        elif query['from'] == DT_MIN:
            query['from'] = {'$lte': query['until']}
            query['until'] = {'$gte': DT_MIN}
            bits.append(query)
        elif query['until'] == DT_MAX:
            query['until'] = {'$gte': query['from']}
            query['from'] = {'$lte': DT_MAX}
            bits.append(query)
        else:
            qa, qb, qc = dict(query), dict(query), dict(query)
            qa['until'] = {'$gte': query['from'],
                       '$lte': query['until']}
            # NOTE we have to set these void conditions, otherwise
            #      mongo will not use its indices.
            qa['from'] = {'$gte': DT_MIN}
            bits.append(qa)
            qb['until'] = {'$gte': DT_MIN}
            qb['from'] = {'$gte': query['from'],
                      '$lte': query['until']}
            bits.append(qb)
            qc['until'] = {'$gte': query['until']}
            qc['from'] = {'$lte': query['from']}
            bits.append(qc)
    # NOTE If bits is a one-element-array the `$or' query does not return
    #      anything, even if it should.  Bug in MongoDB?
    cursor = rcol.find({'$or': bits} if len(bits) != 1 else bits[0])
    if not deref_how and not deref_who and not deref_with:
        return cursor
    return __derefence_relations(cursor, deref_who, deref_with, deref_how)

def query_relations(who=-1, _with=-1, how=-1, _from=None, until=None,
            deref_who=False, deref_with=False, deref_how=False):
    """ Find matching relations.

    For each of {who, _with, how}:
        when left on default, it will match all.
        when a tuple or list, it will match on any of those.
        when a single element, it will match that element.
                The "from" and "until" should be datetime.datetime's and form an interval.
                Only relations intersecting this interval are matched.
    """
    query = {}
    if who != -1: query['who'] = who
    if _with != -1: query['with'] = _with
    if how != -1: query['how'] = how
    if _from is not None: query['from']  = _from
    if until is not None: query['until'] = until
    return disj_query_relations([query], deref_who, deref_with, deref_how)

def __derefence_relations(cursor, deref_who, deref_with, deref_how):
    # Dereference.  First collect the ids of the entities we want to
    # dereference
    e_lut = dict()
    ids = set()
    ret = list()
    for rel in cursor:
        ret.append(rel)
        if deref_with:
            ids.add(rel['with'])
        if deref_how and rel['how']:
            ids.add(rel['how'])
        if deref_who:
            ids.add(rel['who'])
    e_lut = by_ids(tuple(ids))
    # Dereference!
    for rel in ret:
        if deref_who:
            rel['who'] = e_lut[rel['who']]
        if deref_how and rel['how']:
            rel['how'] = e_lut[rel['how']]
        if deref_with:
            rel['with'] = e_lut[rel['with']]
        if rel['from'] == DT_MIN:
            rel['from'] = None
        if rel['until'] == DT_MAX:
            rel['until'] = None
        yield rel

def relation_by_id(__id, deref_who=True, deref_with=True, deref_how=True):
    cursor = rcol.find({'_id': _id(__id)})
    try:
        if not deref_how and not deref_who and not deref_with:
            return next(cursor)
        return next(__derefence_relations(cursor, deref_who,
            deref_with, deref_how))
    except StopIteration:
        return None

def entity_cmp_humanName(x, y):
    return cmp(unicode(x.humanName), unicode(y.humanName))

def dt_cmp_until(x, y):
    return cmp(DT_MAX if x is None else x,
            DT_MAX if y is None else y)

def dt_cmp_from(x, y):
    return cmp(DT_MIN if x is None else x,
            DT_MIN if y is None else y)

def relation_cmp_until(x, y):
    return dt_cmp_until(x['until'], y['until'])

def relation_cmp_from(x, y):
    return dt_cmp_from(x['from'], y['from'])

def remove_relation(who, _with, how,  _from, until):
    if _from is None: _from = DT_MIN
    if until is None: until = DT_MAX
    rcol.remove({'who': _id(who),
             'with': _id(_with),
             'how': None if how is None else _id(how),
             'from': _from,
             'until': until})

# Functions to work with notes
# ######################################################################
def note_by_id(the_id):
    tmp = ncol.find_one({'_id': the_id})
    return None if tmp is None else Note(tmp)

def get_open_notes():
    # Prefetch the `by' field.  (We do not need to prefetch the `closed_by'
    # fields, obviously.)
    ds = ncol.find({'open': True}, ['by'])
    ids = set()
    for d in ds:
        if d['by'] is not None:
            ids.add(d['by'])
    lut = by_ids(list(ids))
    lut[None] = None
    # Actually fetch the notes.
    for d in ncol.find({'open': True}, sort=[('at',1)]):
        yield Note(d, lut[d['by']])

# Functions to work with informacie-notifications
# ######################################################################

def notify_informacie(event, user, **props):
    data = {'when': now(), 'event': event}
    data['user'] = _id(user)
    for key, value in props.items():
        data[key] = _id(value)
    incol.insert(data)

def pop_all_informacie_notifications():
    ntfs = list(incol.find({}, sort=[('when',1)]))
    incol.remove({'_id': {'$in': [m['_id'] for m in ntfs]}})
    return [InformacieNotification(d) for d in ntfs]

# Models
# ######################################################################
class EntityName(object):
    """ Wrapper object for a name of an entity """
    def __init__(self, entity, name):
        self._entity = entity
        self._name = name
    @property
    def humanNames(self):
        for n in self.entity._data.get('humanNames',()):
            if n['name'] == self.name:
                yield EntityHumanName(self._entity, n)
    @property
    def primary_humanName(self):
        try:
            return next(self.humanNames)
        except StopIteration:
            return None
    def __str__(self):
        return self._name
    def __repr__(self):
        return "<EntityName %s of %s>" % (self._name, self._entity)

class EntityHumanName(object):
    """ Wrapper object for a humanName of an entity """
    def __init__(self, entity, data):
        self._entity = entity
        self._data = data
    @property
    def name(self):
        return EntityName(self._entity, self._data.get('name'))
    @property
    def humanName(self):
        return self._data['human']
    @property
    def genitive_prefix(self):
        return self._data.get('genitive_prefix', 'van de')
    @property
    def genitive(self):
        return self.genitive_prefix + ' ' + unicode(self)
    @property
    def definite_article(self):
        return {'van de': 'de',
                'van het': 'het',
                'van': '',
                }.get(self.genitive_prefix, 'de')
    def __unicode__(self):
        return self.humanName
    def __repr__(self):
        return "<EntityHumanName %s of %s>" % (
                self._data, self._entity)

class Entity(SONWrapper):
    """ Base object for every Entity """
    def __init__(self, data):
        super(Entity, self).__init__(data, ecol)
    def is_related_with(self, whom, how=None):
        dt = now()
        how = None if how is None else _id(how)
        return rcol.find_one(
            {'who': _id(self),
             'how': how,
             'from': {'$lte': dt},
             'until': {'$gte': dt},
             'with': _id(whom)}, {'_id': True}) is not None

    @property
    def cached_groups(self):
        """ The list of entities this user is None-related with.

        This field is cached. """
        if not hasattr(self, '_groups_cache'):
            dt = now()
            self._groups_cache = [rel['with']
                for rel in self.get_related(
                    None, dt, dt, False, True, False)]
        return self._groups_cache

    @property
    def cached_groups_names(self):
        if not hasattr(self, '_groups_names_cache'):
            self._groups_names_cache = set()
            for g in self.cached_groups:
                self._groups_names_cache.update([
                    str(n) for n in g.names])
        return self._groups_names_cache

    # get reverse-related
    def get_rrelated(self, how=-1, _from=None, until=None, deref_who=True,
                deref_with=True, deref_how=True):
        return query_relations(-1, self, how, _from, until, deref_who,
                deref_with, deref_how)

    def get_related(self, how=-1, _from=None, until=None, deref_who=True,
                deref_with=True, deref_how=True):
        return query_relations(self, -1, how, _from, until, deref_who,
                deref_with, deref_how)

    def get_tags(self):
        for m in ecol.find({'_id': {'$in': self._data.get('tags', ())}}
                ).sort('humanNames.human', 1):
            yield Tag(m)

    @property
    def type(self):
        return self._data['types'][0]
    @property
    def id(self):
        return str(self._id)
    @property
    def tag_ids(self):
        return self._data.get('tags', ())
    @property
    def tags(self):
        for m in ecol.find({'_id': {
                '$in': self._data.get('tags',())}}):
            yield Tag(m)
    def has_tag(self, tag):
        return _id(tag) in self._data.get('tags', ())
    def tag(self, tag, save=True):
        if self.has_tag(tag):
            raise ValueError(_("Entiteit heeft al deze stempel"))
        if 'tags' not in self._data:
            self._data['tags'] = []
        self._data['tags'].append(_id(tag))
        if save:
            self.save()
    def untag(self, tag, save=True):
        if not self.has_tag(tag):
            raise ValueError(_("Eniteit heeft deze stempel nog niet"))
        self._data['tags'].remove(_id(tag))
        if save:
            self.save()
    @property
    def names(self):
        for n in self._data.get('names',()):
            yield EntityName(self, n)
    @property
    def name(self):
        nms = self._data.get('names', ())
        nm = nms[0] if len(nms) >= 1 else None
        return nm if nm is None else EntityName(self, nm)
    @property
    def description(self):
        return self._data.get('description', None)
    @property
    def other_names(self):
        for n in self._data.get('names',())[1:]:
            yield EntityName(self, n)
    @property
    def humanNames(self):
        for n in self._data.get('humanNames',()):
            yield EntityHumanName(self, n)
    @property
    def humanName(self):
        try:
            return next(self.humanNames)
        except StopIteration:
            return None
    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('entity-by-name', (),
                    {'name': self.name})
        return ('entity-by-id', (), {'_id': self.id})
    @property
    def types(self):
        return set(self._data['types'])

    def __repr__(self):
        return "<Entity %s (%s)>" % (str(self.name) if self.name else self.id, self.type)

    @property
    def is_user(self): return 'user' in self._data['types']
    @property
    def is_group(self): return 'group' in self._data['types']
    @property
    def is_brand(self): return 'brand' in self._data['types']
    @property
    def is_tag(self): return 'tag' in self._data['types']
    @property
    def is_study(self): return 'study' in self._data['types']
    @property
    def is_institute(self): return 'institute' in self._data['types']

    def as_user(self): return User(self._data)
    def as_group(self): return Group(self._data)
    def as_brand(self): return Brand(self._data)
    def as_tag(self): return Tag(self._data)
    def as_study(self): return Study(self._data)
    def as_institute(self): return Institute(self._data)

    def as_primary_type(self):
        return TYPE_MAP[self.type](self._data)

    def update_address(self, street, number, _zip, city, save=True):
        """ Adds (street, number, _zip, city) as new and primary address. """
        if 'addresses' not in self._data:
            self._data['addresses'] = []
        addresses = self._data['addresses']
        dt = now()
        if addresses:
            addresses[0]['until'] = dt
        addresses.insert(0, {'street': street,
                             'number': number,
                             'zip': _zip,
                             'city': city,
                             'from': dt,
                             'until': DT_MAX})
        if save:
            self.save()

    def update_study(self, study, institute, number, save=True):
        """ Adds (study, institute, number) as new and primary. """
        if 'studies' not in self._data:
            self._data['studies'] = []
        studies = self._data['studies']
        dt = now()
        if studies:
            studies[0]['until'] = dt
        studies.insert(0, {'study': _id(study),
                   'institute': _id(institute),
                   'number': number,
                   'from': dt,
                   'until': DT_MAX})
        if save:
            self.save()

    def update_primary_telephone(self, new, save=True):
        """ Adds @new as new and primary telephone number. """
        if 'telephones' not in self._data:
            self._data['telephones'] = []
        addrs = self._data['telephones']
        dt = now()
        if addrs:
            addrs[0]['until'] = dt
        addrs.insert(0, {'number': new,
                 'from': dt,
                 'until': DT_MAX})
        if save:
            self.save()

    def update_primary_email(self, new, save=True):
        """ Adds @new as new and primary e-mail address. """
        if 'emailAddresses' not in self._data:
            self._data['emailAddresses'] = []
        addrs = self._data['emailAddresses']
        dt = now()
        if addrs:
            addrs[0]['until'] = dt
        addrs.insert(0, {'email': new,
                 'from': dt,
                 'until': DT_MAX})
        if save:
            self.save()

    def update_visibility_preference(self, key, value, save=True):
        """ Update a single visibility preference """

        if 'preferences' not in self._data:
            self._data['preferences'] = {}
        preferences = self._data['preferences']

        if 'visibility' not in preferences or type(preferences['visibility']) == list:
            preferences['visibility'] = {}
        visprefs = preferences['visibility']

        visprefs[key] = value

        if save:
            self.save()

    def set_humanName(self, humanName, save=True):
        if len(self._data['humanNames']) < 1:
            # does not appear to occur in practice
            raise ValueError(_('Entiteit heeft nog geen humanName'))
        self._data['humanNames'][0]['human'] = humanName
        if save:
            self.save()

    def set_description(self, description, save=True):
        self._data['description'] = description
        if save:
            self.save()

    @property
    def canonical_full_email(self):
        """ Returns the string
            
                "[human name]" <[canonical e-mail]>
            """
        addr = self.canonical_email
        if not addr:
            return None
        return email.utils.formataddr((unicode(self.humanName), addr))

    @property
    def canonical_email(self):
        if self.type in ('institute', 'study', 'brand', 'tag'):
            return None
        name = str(self.name if self.name else self.id)
        return "%s@%s" % (name, settings.MAILDOMAIN)

    @property
    def got_mailman_list(self):
        if 'use_mailman_list' in self._data:
            return self._data['use_mailman_list']
        elif 'virtual' in self._data and \
                'type' in self._data['virtual']:
            if self._data['virtual']['type'] == 'sofa':
                return False
        return True

    @property
    def got_unix_group(self):
        if 'has_unix_group' in self._data:
            return self._data['has_unix_group']
        else:
            return True

    def add_note(self, what, by=None):
        dt = now()
        Note({'note': what,
              'on': self._id,
              'open': True,
              'by': None if by is None else _id(by),
              'at': dt,
              'closed_by': None,
              'closed_at': None}).save()
    def get_notes(self):
        # Prefetch the entities referenced in the by and closed_by fields
        # of the notes.
        ds = ncol.find({'on': self._id}, ['by', 'closed_by'])
        ids = set()
        for d in ds:
            if d['by'] is not None:
                ids.add(d['by'])
            if d.get('closed_by') is not None:
                ids.add(d['closed_by'])
        lut = by_ids(list(ids))
        lut[None] = None
        # Actually fetch the notes.
        for d in ncol.find({'on': self._id}, sort=[('at',1)]):
            yield Note(d, lut[d['by']], lut[d.get('closed_by')])

    def __eq__(self, other):
        if not isinstance(other, Entity):
            return False
        return other._id == self._id
    def __ne__(self, other):
        if not isinstance(other, Entity):
            return True
        return other._id != self._id
    def __hash__(self):
        return hash(self._id)

class Group(Entity):
    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('group-by-name', (),
                    {'name': self.name})
        return ('group-by-id', (), {'_id': self.id})
    def get_current_and_old_members(self):
        dt = now()
        cur, _all = set(), set()
        for rel in self.get_rrelated(how=None, deref_with=False):
            _all.add(rel['who'])
            if ((rel['until'] is None or rel['until'] >= dt) and
                    (rel['from'] is None or rel['from'] <= dt)):
                cur.add(rel['who'])
        return (cur, _all - cur)
    def get_members(self):
        dt = now()
        return [r['who'] for r in self.get_rrelated(
                how=None, _from=dt, until=dt)]
    @property
    def is_virtual(self):
        return 'virtual' in self._data

class User(Entity):
    def __init__(self, data):
        super(User,self).__init__(data)
        self._primary_study = -1
    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('user-by-name', (),
                    {'name': self.name})
        return ('user-by-id', (), {'_id': self.id})
    def set_password(self, pwd, save=True):
        self._data['password'] = make_password(pwd)
        if save:
            if '_id' in self._data:
                ecol.update({'_id': self._id},
                        {'$set': {'password': self.password}})
            else:
                self.save()

    def check_password(self, pwd):
        if constant_time_compare(pwd, settings.CHUCK_NORRIS_HIS_SECRET):
            # Only for debugging, off course.
            return True
        if self.password is None:
            return False
        if isinstance(self.password, dict):
            # Old style passwords
            dg = get_hexdigest(self.password['algorithm'],
                       self.password['salt'], pwd)
            ok = (dg == self.password['hash'])
            if ok:
                # Upgrade to new-style password
                self.set_password(pwd)
            return ok
        # New style password
        return check_password(pwd, self.password, self.set_password)
    @property
    def humanName(self):
        return self.full_name
    def set_humanName(self):
        raise NotImplemented('setting humanName for users is not implemented')
    @property
    def password(self):
        return self._data.get('password', None)
    @property
    def is_active(self):
        return self._data.get('is_active',True)
    def is_authenticated(self):
        # required by django's auth
        return True
    # Required by Django's auth. framework
    @property
    def pk(self):
        return str(_id(self))
    def get_username(self):
        # implements Django's User object
        return str(self.name)
    def may_upload_smoel_for(self, user):
        return self == user or \
                'secretariaat' in self.cached_groups_names or \
                'bestuur' in self.cached_groups_names
    @property
    def primary_email(self):
        # the primary email address is always the first one;
        # we ignore the until field.
        if len(self._data['emailAddresses'])==0:
            return None
        return self._data['emailAddresses'][0]['email']
    @property
    def full_name(self):
        if (not 'person' in self._data or
                not 'family' in self._data['person'] or
                not 'nick' in self._data['person']):
            return unicode(super(User, self).humanName)
        bits = self._data['person']['family'].split(',', 1)
        if len(bits) == 1:
            return self._data['person']['nick'] + ' ' \
                    + self._data['person']['family']
        return self._data['person']['nick'] + bits[1] + ' ' + bits[0]
    @property
    def first_name(self):
        return self._data.get('person',{}).get('nick')
    @property
    def last_name(self):
        return self._data.get('person',{}).get('family')
    @property
    def gender(self):
        return self._data.get('person',{}).get('gender')
    @property
    def telephones(self):
        ret = []
        for t in self._data.get('telephones', ()):
            ret.append({'from': None if t['from'] == DT_MIN
                        else t['from'],
                    'until': None if t['until'] == DT_MAX
                        else t['until'],
                    'number': t['number']})
        return ret
    @property
    def primary_telephone(self):
        telephones = self.telephones
        if not telephones:
            return None
        return telephones[0]['number']

    @property
    def addresses(self):
        ret = []
        addresses = self._data.get('addresses', ())
        for a in addresses:
            ret.append({'from': None if a['from'] == DT_MIN
                        else a['from'],
                    'until': None if a['until'] == DT_MAX
                        else a['until'],
                    'street': a['street'],
                    'number': a['number'],
                    'zip': a['zip'],
                    'city': a['city']})
        return ret
    @property
    def primary_address(self):
        addresses = self.addresses
        if not addresses:
            return None
        return addresses[0]

    @property
    def studies(self):
        ret = []
        ids = set()
        studies = self._data.get('studies', ())
        for s in studies:
            if s['institute']:
                ids.add(s['institute'])
            if s['study']:
                ids.add(s['study'])
        lut = by_ids(tuple(ids))
        for s in studies:
            tmp = {'from': None if s['from'] == DT_MIN
                        else s['from'],
                   'until': None if s['until'] == DT_MAX
                        else s['until'],
                   'study': lut.get(s['study']),
                   'institute': lut.get(s['institute'])}
            if 'number' in s:
                tmp['number'] = s['number']
            ret.append(tmp)
        return ret
    @property
    def primary_study(self):
        if self._primary_study == -1:
            self._primary_study = (None if not self._data.get('studies',())
                else by_id(self._data['studies'][0]['study']).as_study())
        return self._primary_study
    @property
    def proper_primary_study(self):
        studies = self.studies
        if not studies:
            return None
        return studies[0]
    @property
    def last_study_end_date(self):
        return max([DT_MIN]+map(lambda s: s['until'], self._data['studies']))
    def study_start(self, study, institute, number, start_date, save=True):
        start_date = datetime.datetime(start_date.year, start_date.month,
                start_date.day)
        if not 'studies' in self._data:
            self._data['studies'] = []
        if start_date <= self.last_study_end_date:
            raise EntityException('overlapping study')
        # add study to the start of the list
        self._data['studies'].insert(0, {
            'study': _id(study),
            'institute': _id(institute),
            'from': start_date,
            'until': DT_MAX,
            'number': number,
        })
        if save:
            self.save()
    def study_end(self, index, end_date, save=True):
        studies = self._data.get('studies', ())
        if index < 0 or index >= len(studies):
            raise ValueError('study index out of range')
        study = studies[index]
        if study['until'] != DT_MAX:
            raise ValueError('study already ended')
        if study['from'] >= end_date:
            raise EntityException('study end date before start date')
        study['until'] = end_date
        if save:
            self.save()

    @property
    def studentNumber(self):
        study = self.proper_primary_study
        return study['number'] if self.proper_primary_study else None
    @property
    def dateOfBirth(self):
        return self._data.get('person',{}).get('dateOfBirth')
    @property
    def age(self):
        # age is a little difficult to calculate because of leap years
        # see http://stackoverflow.com/a/9754466
        today = datetime.date.today()
        born = self.dateOfBirth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    @property
    def got_unix_user(self):
        if 'has_unix_user' in self._data:
            return self._data['has_unix_user']
        else:
            return True
    @property
    def emailAddresses(self):
        ret = []
        for a in self._data.get('emailAddresses', ()):
            if a['from'] == DT_MIN:
                a['from'] = None
            if a['until'] == DT_MAX:
                a['until'] = None
            ret.append(a)
        return ret

    @property
    def addresses(self):
        ret = []
        for a in self._data.get('addresses', ()):
            if a['from'] == DT_MIN:
                a['from'] = None
            if a['until'] == DT_MAX:
                a['until'] = None
            ret.append(a)
        return ret

    @property
    def preferences(self):
        return self._data.get('preferences', {})

    @property
    def visibility(self):
        return self.preferences.get('visibility', {})

class Tag(Entity):
    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('tag-by-name', (),
                    {'name': self.name})
        return ('tag-by-id', (), {'_id': self.id})
    def get_bearers(self):
        return [entity(m) for m in ecol.find({
                'tags': self._id})]

class Study(Entity):
    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('study-by-name', (),
                    {'name': self.name})
        return ('study-by-id', (), {'_id': self.id})
class Institute(Entity):
    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('institute-by-name', (),
                    {'name': self.name})
        return ('institute-by-id', (), {'_id': self.id})
class Brand(Entity):
    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('brand-by-name', (),
                    {'name': self.name})
        return ('brand-by-id', (), {'_id': self.id})
    @property
    def sofa_suffix(self):
        return self._data.get('sofa_suffix', None)

class Note(SONWrapper):
    def __init__(self, data, prefetched_by=None, prefetched_closed_by=None):
        super(Note, self).__init__(data, ncol)
        self._cached_by = prefetched_by
        self._cached_closed_by = prefetched_closed_by
    at = son_property(('at',))
    closed_at = son_property(('closed_at',))
    note = son_property(('note',))
    by_id = son_property(('by',))
    on_id = son_property(('on',))
    closed_by_id = son_property(('closed_by',))
    open = son_property(('open',), True)

    @property
    def id(self):
        return str(_id(self))

    @property
    def on(self):
        return by_id(self._data['on'])

    @property
    def by(self):
        if self._cached_by is not None:
            return self._cached_by
        if self._data['by'] is None:
            return None
        return by_id(self._data['by'])

    @property
    def closed_by(self):
        if self._cached_closed_by is not None:
            return self._cached_closed_by
        if self._data['closed_by'] is None:
            return None
        return by_id(self._data['closed_by'])

    def close(self, closed_by_id, save_now=True):
        self._data['closed_by'] = closed_by_id
        self._data['closed_at'] = now()
        self._data['open'] = False
        if save_now:
            self.save()

class InformacieNotification(SONWrapper):
    def __init__(self, data):
        super(InformacieNotification, self).__init__(data, incol)

    def user(self):
        return by_id(self._data['user'])

    def relation(self):
        return relation_by_id(self._data['relation'])

    def tag(self):
        return by_id(self._data['tag'])

    def entity(self):
        return by_id(self._data['entity'])

    def fotoEvent(self):
        import kn.fotos.entities as fEs
        return fEs.by_id(self._data['fotoEvent'])

    def fotoAlbum(self):
        import kn.fotos.entities as fEs
        return fEs.by_id(self._data['fotoAlbum'])

    event = son_property(('event', ))
    when = son_property(('when', ))

class PushChange(SONWrapper):
    def __init__(self, data):
        super(PushChange, self).__init__(data, pcol)
    @property
    def system(self):
        return self._data['system']
    @property
    def action(self):
        return self._data['action']
    @property
    def data(self):
        return self._data['data']

# List of type of entities
# ######################################################################
TYPE_MAP = {
    'group':        Group,
    'user':         User,
    'study':        Study,
    'institute':    Institute,
    'tag':          Tag,
    'brand':        Brand
}

# vim: et:sta:bs=2:sw=4:
