import datetime
import email.utils
import functools
import hashlib
import os
import re
import typing
from typing import Optional, Tuple, Set, List, Dict, Iterator, Sequence, Iterable, Any, TypeVar, Union, Callable

import PIL.Image
import pymongo.cursor

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.signals import user_logged_in
from django.core.files.storage import default_storage
from django.db.models import permalink
from django.utils import six
from django.utils.crypto import constant_time_compare
from django.utils.six.moves import range
from django.utils.translation import ugettext as _

from kn.base.conf import DT_MAX, DT_MIN
from kn.fotos.utils import resize_proportional
from kn.leden.date import now
from kn.leden.mongo import SONWrapper, _id, db, son_property

# ######################################################################
# The collections
# ######################################################################
ecol = db['entities']   # entities: users, group, tags, studies, ...

EntityID = typing.NewType('EntityID', str)
PermalinkType = Tuple[str, Any, Dict[str, str]]
# Example of a user
# ----------------------------------------------------------------------
# {"_id" : ObjectId("4e6fcc85e60edf3dc0000270"),
#  "address" : { "city" : "Nijmegen",
#                "zip" : "...",
#                "number" : "...",
#                "street" : "..." },
#   "types" : [ "user" ],
#   "names" : [ "giedo" ],
#   "humanNames" : [ { "human" : "Giedo Jansen" } ],
#   "person" : { "given" : null,
#                "family" : "Jansen",
#                "nick" : "Giedo",
#                "dateOfBirth" : ISODate("..."),
#                "titles" : [ ] },
#   "is_underage" : false,
#   "is_active" : 0,
#   "email" : "...",
#   "password" : "pbkdf2_sha256$15000$...$...",
#   "studies" : [ { "institute" : ObjectId("4e6fcc85e60edf3dc000001d"),
#                   "study" : ObjectId("4e6fcc85e60edf3dc0000030"),
#                   "number" : "...",
#                   "from" : ...,
#                   "until" : DT_MAX } ],
#   "telephone" : "...",
#   "preferred_language": "nl",
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

# relations: "giedo is chairman of bestuur from
#             date A until date B"
rcol = db['relations']

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
#   "note" : "Adres veranderd. Was:  (...) Nijmegen",
#   "at" : ISODate("2011-03-24T00:00:00Z"),
#   "by" : ObjectId("4e6fcc85e60edf3dc0000410")
# }

# human readable list of notifications for informacie group
incol = db['informacie_notifications']
# TODO add example


def get_hexdigest(algorithm: str, salt: bytes, raw_password: bytes) -> str:
    """ Used to check old-style passwords. """
    assert algorithm == 'sha1'
    return hashlib.sha1(salt + raw_password).hexdigest()


def ensure_indices() -> None:
    """ Ensures that the indices we need on the collections are set """
    # entities
    # NOTE On some versions of Mongo, a unique sparse index does not allow
    #      more than one entitity without a name.
    # ecol.ensure_index('names', unique=True, sparse=True)
    # XXX: ensure_index is deprecated, use create_index
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
    rcol.ensure_index([('until', 1),
                       ('from', -1)])
    # notes
    ncol.ensure_index([('on', 1),
                       ('at', 1)])
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

AnyEntityType = typing.Union["Group", "User", "Study", "Institute", "Tag", "Brand", "Entity"]
@typing.overload
def entity(d: None) -> None: ...
@typing.overload
def entity(d: Dict[str, typing.Any]) -> AnyEntityType: ...
def entity(d: Optional[Dict[str, typing.Any]]) -> Optional[AnyEntityType]:
    """ Given a dictionary, returns an Entity object wrapping it """
    if d is None:
        return None
    t = d['types'][0]
    if t in TYPE_MAP:
        return TYPE_MAP[t](d)
    raise TypeError("unknown type", t)

I = TypeVar('I')
R = TypeVar('R')
class CursorMapper(typing.Generic[I, R]):
    """ Wrap a mongo cursor to map the results to an entity type """
    def __init__(self, cursor: pymongo.cursor.Cursor, mapper: typing.Callable[[I], R]) -> None:
        self._cursor = cursor
        self._mapper = mapper
    def __getattr__(self, attr: str) -> Any:
        return getattr(self._cursor, attr)
    def __getitem__(self, index: Union[int, slice]) -> Union["CursorMapper[I, R]", R]:
        if type(index) is slice:
            return CursorMapper(self._cursor.__getitem__(index), self._mapper)
        else:
            return self._mapper(self._cursor.__getitem__(index))
    def __next__(self) -> R:
        return self._mapper(self._cursor.__next__())
    def sort(self, *arg: List[Any], **kwarg: Dict[str, Any]) -> "CursorMapper[I, R]":
        self._cursor.sort(*arg, **kwarg)
        return self
    def clone(self) -> "CursorMapper[I, R]":
        return CursorMapper(self._cursor.clone(), self._mapper)
    def next(self) -> R:
        return self._mapper(self._cursor.next())

def of_type(t: str) -> Iterator["Entity"]: # AnyEntityType
    """ Returns all entities of type @t """
    return CursorMapper(ecol.find({'types': t}), TYPE_MAP[t])


def of_type_by_name(t: str) -> Dict[str, AnyEntityType]:
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


def by_ids(ns: Sequence[EntityID]) -> Dict[EntityID, AnyEntityType]:
    """ Find entities by a list of _ids """
    ret = {}
    for m in ecol.find({'_id': {'$in': ns}}):
        ret[m['_id']] = entity(m)
    return ret


__id2name_cache: Dict[str, EntityID]
__id2name_cache = {}


def id_by_name(n: str, use_cache: bool=False) -> Optional[EntityID]:
    """ Find the _id of entity with name @n """
    ret = None
    if use_cache:
        if n in __id2name_cache:
            ret = __id2name_cache[n]
    if ret is None:
        obj = ecol.find_one({'names': n}, {'names': 1})
        if obj is None:
            return None
        ret = obj['_id']
        if use_cache and ret is not None:
            __id2name_cache[n] = ret
    return ret


def ids_by_names(ns: Optional[List[str]]=None, use_cache:bool=False) -> Dict[str, EntityID]:
    """ Finds _ids of entities by a list of names """
    ret = {}
    nss = None if ns is None else frozenset(ns)
    if use_cache and nss is not None:
        nss2 = set(nss)
        for n in nss:
            if n in __id2name_cache:
                ret[n] = __id2name_cache[n]
                nss2.remove(n)
        nss = frozenset(nss2)
    for m in ecol.find({} if nss is None else
                       {'names': {'$in': tuple(nss)}}, {'names': 1}):
        for n in m.get('names', ()):
            if nss is None or n in nss:
                ret[n] = m['_id']
                if use_cache and ns is not None:
                    __id2name_cache[n] = m['_id']
                continue
    return ret


def by_names(ns: List[str]) -> Dict[str, 'Entity']:
    """ Finds entities by a list of names """
    ret = {}
    nss = frozenset(ns)
    for m in ecol.find({'names': {'$in': ns}}):
        for n in m['names']:
            if n in nss:
                ret[n] = entity(m)
                continue
    return ret


def by_name(n: str) -> typing.Optional[AnyEntityType]:
    """ Finds an entity by name """
    return entity(ecol.find_one({'names': n}))


def by_id(n: EntityID) -> typing.Optional[AnyEntityType]:
    """ Finds an entity by id """
    if n is None:
        return None
    return entity(ecol.find_one({'_id': _id(n)}))


def by_study(study: "Study") -> Iterator[AnyEntityType]:
    """ Finds entities by studies.study """
    for m in ecol.find({'studies.study': _id(study)}):
        yield entity(m)


def by_institute(institute: "Institute") -> Iterator["Entity"]:
    """ Finds entities by studies.insitute """
    for m in ecol.find({'studies.institute': _id(institute)}):
        yield entity(m)


def get_years_of_birth() -> range:
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
    return range(start, end + 1)


def by_year_of_birth(year: int) -> Iterator["Entity"]:
    """ Finds entities by year of birth """
    for m in ecol.find({'types': 'user',
                        'person.dateOfBirth': {
                            '$lt': datetime.datetime(year + 1, 1, 1),
                            '$gte': datetime.datetime(year, 1, 1)}}):
        yield entity(m)


def all() -> Iterator[AnyEntityType]:
    """ Finds all entities """
    for m in ecol.find():
        yield entity(m)


def names_by_ids(ids: Optional[EntityID]=None) -> Dict[EntityID, Optional[str]]:
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


def ids() -> Set[EntityID]:
    """ Returns a set of all ids """
    ret: Set[EntityID] = set()
    for e in ecol.find({}, {'_id': True}):
        ret.add(e['_id'])
    return ret


def names() -> Set[str]:
    """ Returns a set of all names """
    ret: Set[str] = set()
    for e in ecol.find({}, {'names': True}):
        ret.update(e.get('names', ()))
    return ret

# Searching entities by keywords
# ######################################################################


def by_keyword(keyword: str, limit: int=20, _type: Optional[str]=None) -> List["AnyEntityType"]:
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
    query_dict: Dict[str, typing.Any] = {'humanNames.human': {
        '$regex': regex, '$options': 'i'}}
    if _type:
        query_dict['types'] = _type
    cursor = ecol.find(query_dict, limit=(0 if limit is None else limit),
                       sort=[('humanNames.human', 1)])
    return [entity(x) for x in cursor]

# Specialized functions to work with entities.
# ######################################################################

T = typing.TypeVar('T')
def bearers_by_tag_id(tag_id: EntityID, _as: typing.Callable[..., T]=entity) -> List[T]:
    """ Find the bearers of the tag with @tag_id """
    return [_as(x) for x in ecol.find({'tags': tag_id})]


def year_to_range(year: int) -> Tuple[datetime.datetime, datetime.datetime]:
    """ Returns (start_date, end_date) for the given year """
    return (datetime.datetime(2003 + year, 9, 1),
            datetime.datetime(2004 + year, 8, 31))


def date_to_year(dt: datetime.datetime) -> int:
    """ Returns the `verenigingsjaar' at the date """
    year = dt.year - 2004
    if dt.month >= 9:
        year += 1
    if year < 1:
        year = 1
    return year

def quarter_to_range(quarter: int) -> Tuple[datetime.datetime, datetime.datetime]:
    """ Translates a quarter to a start and end datetime.
        The quarters of the first year are [1,2,3,4]. """
    startCMonths = (quarter - 1) * 3 + 8
    startYears, startMonths = divmod(startCMonths, 12)
    start = datetime.datetime(2004 + startYears, startMonths + 1, 1)
    endCMonths = quarter * 3 + 8
    endYears, endMonths = divmod(endCMonths, 12)
    end = (datetime.datetime(2004 + endYears, endMonths + 1, 1)
           - datetime.timedelta(1))
    return start, end

# Functions to work with relations
# ######################################################################

Relation = typing.NewType("Relation", Dict[str, typing.Any])
class Relation_(object):
    from_: Optional[datetime.datetime]
    until: Optional[datetime.datetime]
    with_: Optional[Union["Entity", EntityID]]
    how: Optional[Union["Entity", EntityID]]
    who: Union["Entity", EntityID]

    def is_active_at(dt: datetime.datetime) -> bool:
        """ Returns whether @rel is active at @dt """
        return ((self.until is None or self.until >= dt)
                and (self.from_ is None or self.from_ <= dt))

    is_virtual: bool
    @property
    def is_virtual(self) -> bool:
        """ Returns whether @rel is "virtual".
        
        Requires rel['with'] to be deref'd """
        return bool(self.with_.is_group and self.with_.as_group().is_virtual)

    is_active: bool
    @property
    def is_active(self) -> bool:
        return self.is_active_at(now())

    def may_end(user: "User") -> bool:
        """ Returns whether @user may end @rel """
        if self.is_virtual:
            return False
        if not self.is_active:
            return False
        if 'secretariaat' in user.cached_groups_names:
            return True
        if _id(self.who) == _id(user) and \
           self.how is None and \
           by_id(self.with_).has_tag_name('!free-to-join'):
            return True
        return False

    def __init__(self, dct: Dict[str, Any]):
        self.from_ = dct['from']
        self.until = dct['until']
        self.with_ = dct['with']
        self.how = dct['how']
        self.who = dct['who']
        
def relation_is_active_at(rel: Relation, dt: datetime.datetime) -> bool:
    """ Returns whether @rel is active at @dt """
    return ((rel['until'] is None or rel['until'] >= dt)
            and (rel['from'] is None or rel['from'] <= dt))


def relation_is_active(rel: Relation) -> bool:
    """ Returns whether @rel is active now """
    return relation_is_active_at(rel, now())


def relation_is_virtual(rel: Relation) -> bool:
    """ Returns whether @rel is "virtual".

        Requires rel['with'] to be deref'd """
    return bool(rel['with'].is_group and rel['with'].as_group().is_virtual)


def user_may_end_relation(user: "User", rel: Relation) -> bool:
    """ Returns whether @user may end @rel """
    if relation_is_virtual(rel):
        return False
    if not relation_is_active(rel):
        return False
    if 'secretariaat' in user.cached_groups_names:
        return True
    if _id(rel['who']) == _id(user) and \
            rel['how'] is None and \
            by_id(rel['with']).has_tag_name('!free-to-join'):
        return True
    return False


def end_relation(__id: EntityID) -> None:
    dt = now()
    rcol.update({'_id': _id(__id)}, {'$set': {'until': dt}})


def user_may_begin_relation(user: "EntityID", who: "EntityID", _with: "EntityID", how: Optional[str]) -> bool:
    """ Returns whether @user may begin a @how-relation between @who and @_with
    """
    _with_e = by_id(_with)
    user_e = by_id(user)
    if _with_e.is_group and _with_e.as_group().is_virtual:
        return False
    if 'secretariaat' in user_e.cached_groups_names:
        return True
    if _with_e.has_tag_name('!free-to-join'):
        if _id(user) == _id(who) and how is None:
            return True
    return False


def add_relation(who: "Entity", _with: "Entity", how: Optional[str]=None, _from: Optional[datetime.datetime]=None, until: Optional[datetime.datetime]=None) -> Relation:
    if _from is None:
        _from = DT_MIN
    if until is None:
        until = DT_MAX
    return Relation(rcol.insert({'who': _id(who),
                        'with': _id(_with),
                        'how': None if how is None else _id(how),
                        'from': _from,
                        'until': until}))


def user_may_tag(user: "Entity", group: "Entity", tag: "Entity") -> bool:
    return bool('secretariaat' in user.cached_groups_names)


def user_may_untag(user: "Entity", group: "Entity", tag: "Entity") -> bool:
    return bool('secretariaat' in user.cached_groups_names)


def disj_query_relations(queries:Iterable[Any], deref: set) -> Iterable[Relation]:
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
                query[attr] = {'$in': [_id(x) for x in query[attr]]}
            elif query[attr] is not None:
                query[attr] = _id(query[attr])
            else:
                query[attr] = None
        if query.get('from') is None:
            query['from'] = DT_MIN
        if query.get('until') is None:
            query['until'] = DT_MAX
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
    if deref == set():
        return cursor
    return __derefence_relations(cursor, deref)


RelQuery = typing.Union[int, Sequence[EntityID], EntityID, 'Entity']
def query_relations(who: RelQuery=-1, _with: RelQuery=-1, how: RelQuery=-1,
                    _from: Optional[datetime.datetime]=None, until: Optional[datetime.datetime]=None,
                    deref: set = set()) -> Iterable[Relation]:
    """ Find matching relations.

    For each of {who, _with, how}:
        when left on default, it will match all.
        when a tuple or list, it will match on any of those.
        when a single element, it will match that element.
                The "from" and "until" should be datetime.datetime's
                    and form an interval.
                Only relations intersecting this interval are matched.
    """
    query: Dict[str, Any] = {}
    if who != -1:
        query['who'] = who
    if _with != -1:
        query['with'] = _with
    if how != -1:
        query['how'] = how
    if _from is not None:
        query['from'] = _from
    if until is not None:
        query['until'] = until
    return disj_query_relations([query], deref)


def __derefence_relations(cursor: Iterable[Relation], deref: set) -> Iterator[Relation]:
    # Dereference.  First collect the ids of the entities we want to
    # dereference
    e_lut: Dict[EntityID, AnyEntityType] = dict()
    ids = set()
    ret = list()
    for rel in cursor:
        ret.append(rel)
        for what in deref:
            if rel[what]:
                ids.add(rel[what])
    e_lut = by_ids(tuple(ids))
    # Dereference!
    for rel in ret:
        for what in deref:
            if rel[what]:
                rel[what] = e_lut[rel[what]]
        if rel['from'] == DT_MIN:
            rel['from'] = None
        if rel['until'] == DT_MAX:
            rel['until'] = None
        yield Relation(rel)


def relation_by_id(__id, deref=set(("who", "how", "what"))):
    cursor = rcol.find({'_id': _id(__id)})
    try:
        if not deref:
            return next(cursor)
        return next(__derefence_relations(cursor, deref))
    except StopIteration:
        return None

@typing.overload
def entity_humanName(x: None) -> None: ...
@typing.overload
def entity_humanName(x: "Entity") -> str: ...
def entity_humanName(x: Optional["Entity"]) -> Optional[str]:
    """ Returns the human name of an entity or None if None is given.
        Useful for the key argument in a sort function. """
    return None if x is None else six.text_type(x.humanName)


def dt_until(x: Optional[datetime.datetime]) -> datetime.datetime:
    """ Treat a datetime from the db as one which is used as an until-date:
        None is interpreted as DT_MAX. Useful for sorting. """
    return x if x else DT_MAX


def dt_from(x: Optional[datetime.datetime]) -> datetime.datetime:
    """ Treat a datetime from the db as one which is used as an from-date:
        None is interpreted as DT_MIN. Useful for sorting. """
    return x if x else DT_MIN


def relation_until(x: Relation) -> datetime.datetime:
    """ Returns the datetime until the given relations holds.
        Useful as `key' argument for sort functions. """
    return dt_until(x['until'])


def relation_from(x: Relation) -> datetime.datetime:
    """ Returns the datetime from which the given relations holds.
        Useful as `key' argument for sort functions. """
    return dt_from(x['from'])


def remove_relation(who, _with, how, _from, until) -> None:
    if _from is None:
        _from = DT_MIN
    if until is None:
        until = DT_MAX
    # XXX: .remove is deprecated
    rcol.remove({'who': _id(who),
                 'with': _id(_with),
                 'how': None if how is None else _id(how),
                 'from': _from,
                 'until': until})

# Functions to work with informacie-notifications
# ######################################################################


def notify_informacie(event: str, user: "User", **props) -> None:
    data = {'when': now(), 'event': event}
    data['user'] = _id(user)
    for key, value in props.items():
        data[key] = _id(value)
    incol.insert(data)


def pop_all_informacie_notifications() -> typing.List['InformacieNotification']:
    ntfs = list(incol.find({}, sort=[('when', 1)]))
    incol.remove({'_id': {'$in': [m['_id'] for m in ntfs]}})
    return [InformacieNotification(d) for d in ntfs]

# Models
# ######################################################################

class EntityName(object):

    """ Wrapper object for a name of an entity """

    def __init__(self, entity: "Entity", name: str) -> None:
        self._entity = entity
        self._name = name

    humanNames: Iterator['EntityHumanName']
    @property
    def humanNames(self):
        for n in self._entity._data.get('humanNames', ()):
            if n['name'] == self._name:
                yield EntityHumanName(self._entity, n)

    primary_humanName: typing.Optional['EntityHumanName']
    @property
    def primary_humanName(self):
        try:
            return next(self.humanNames)
        except StopIteration:
            return None

    name: str
    @property
    def name(self) -> str:
        return self._name

    def __str__(self) -> str:
        return self._name

    def __repr__(self):
        return "<EntityName %s of %s>" % (self._name, self._entity)


@six.python_2_unicode_compatible
class EntityHumanName(object):

    """ Wrapper object for a humanName of an entity """

    def __init__(self, entity: "Entity", data: Dict[str, str]) -> None:
        self._entity = entity
        self._data = data

    name: EntityName
    @property
    def name(self):
        return EntityName(self._entity, self._data.get('name'))

    humanName: str
    @property
    def humanName(self):
        return self._data['human']

    genitive_prefix: str
    @property
    def genitive_prefix(self):
        return self._data.get('genitive_prefix', 'van de')

    genitive: str
    @property
    def genitive(self):
        return self.genitive_prefix + ' ' + six.text_type(self)

    definite_article: str
    @property
    def definite_article(self):
        return {'van de': 'de',
                'van het': 'het',
                'van': '',
                }.get(self.genitive_prefix, 'de')

    def __str__(self):
        return self.humanName

    def __repr__(self):
        return "<EntityHumanName %s of %s>" % (
            self._data, self._entity)


class Entity(SONWrapper):

    """ Base object for every Entity """

    @classmethod
    def all(cls):
        if getattr(cls, 'db_typename'):
            return of_type(cls.db_typename)
        return all()

    @classmethod
    def by_name(cls, name):
        if getattr(cls, 'db_typename'):
            raise NotImplementedError
            # return of_type_by_name(cls.db_typename, name)
        return by_name(name)

    def __init__(self, data: Dict[str, typing.Any]) -> None:
        super(Entity, self).__init__(data, ecol)

    def is_related_with(self, whom: 'Entity', how: Optional[str]=None) -> bool:
        dt = now()
        how = None if how is None else _id(how)
        return rcol.find_one(
            {'who': _id(self),
             'how': how,
             'from': {'$lte': dt},
             'until': {'$gte': dt},
             'with': _id(whom)}, {'_id': True}) is not None

    cached_groups: typing.List['Group']
    @property
    def cached_groups(self):
        """ The list of entities this user is None-related with.

        This field is cached. """
        if not hasattr(self, '_groups_cache'):
            dt = now()
            self._groups_cache = [rel['with']
                                  for rel in self.get_related(
                                          None, dt, dt, deref=set(("with",)))]
        return self._groups_cache

    cached_groups_names: typing.Set[str]
    @property
    def cached_groups_names(self):
        if not hasattr(self, '_groups_names_cache'):
            self._groups_names_cache: Set[str] = set()
            for g in self.cached_groups:
                self._groups_names_cache.update([
                    str(n) for n in g.names])
        return self._groups_names_cache

    # get reverse-related
    def get_rrelated(self, how=-1, _from: Optional[datetime.datetime]=None, until=None, deref: set = set(("who", "how", "with"))) -> Iterable[Relation]:
        return query_relations(-1, self, how, _from, until, deref)

    def get_related(self, how=-1, _from=None, until=None, deref: set = set(("who", "how", "with"))) -> Iterable[Relation]:
        return query_relations(self, -1, how, _from, until, deref)

    def get_tags(self) -> Iterator['Tag']:
        for m in ecol.find({'_id': {'$in': self._data.get('tags', ())}}
                           ).sort('humanNames.human', 1):
            yield Tag(m)

    @property
    def type(self):
        return self._data['types'][0]

    id: EntityID
    @property
    def id(self):
        return EntityID(str(self._id))

    tag_ids: Iterator[EntityID]
    @property
    def tag_ids(self):
        return self._data.get('tags', ())

    tags: Iterator['Tag']
    @property
    def tags(self) -> Iterable['Tag']:
        return CursorMapper(ecol.find({'_id': {
                '$in': self._data.get('tags', ())}}), Tag)

    def has_tag(self, tag: typing.Union["Tag", EntityID]) -> bool:
        return bool(_id(tag) in self._data.get('tags', ()))

    def has_tag_name(self, tag: str) -> bool:
        t = id_by_name(tag, True)
        return self.has_tag(t) if t else False

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

    names: Iterator[EntityName]
    @property
    def names(self):
        for n in self._data.get('names', ()):
            yield EntityName(self, n)

    name: typing.Optional[EntityName]
    @property
    def name(self):
        nms = self._data.get('names', ())
        nm = nms[0] if len(nms) >= 1 else None
        return nm if nm is None else EntityName(self, nm)

    description: typing.Optional[str]
    @property
    def description(self):
        return self._data.get('description', None)

    other_names: Iterator[EntityName]
    @property
    def other_names(self):
        for n in self._data.get('names', ())[1:]:
            yield EntityName(self, n)

    humanNames: Iterator[EntityHumanName]
    @property
    def humanNames(self):
        for n in self._data.get('humanNames', ()):
            yield EntityHumanName(self, n)

    humanName: typing.Optional[EntityHumanName]
    @property
    def humanName(self):
        try:
            return next(self.humanNames)
        except StopIteration:
            return None

    @permalink
    def get_absolute_url(self) -> PermalinkType:
        if self.name:
            return ('entity-by-name', (),
                    {'name': self.name})
        return ('entity-by-id', (), {'_id': self.id})

    @property
    def types(self):
        return set(self._data['types'])

    def __repr__(self):
        return "<Entity %s (%s)>" % (
            str(self.name) if self.name else self.id, self.type)

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

    def as_user(self)  -> "User": return User(self._data)

    def as_group(self) -> "Group": return Group(self._data)

    def as_brand(self) -> "Brand": return Brand(self._data)

    def as_tag(self)   -> "Tag": return Tag(self._data)

    def as_study(self) -> "Study": return Study(self._data)

    def as_institute(self) -> "Institute": return Institute(self._data)

    def as_primary_type(self) -> AnyEntityType:
        return TYPE_MAP[self.type](self._data)

    def update_address(self, street, number, _zip, city, save=True):
        """ Sets (street, number, _zip, city) as address. """
        self._data['address'] = {
            'street': street,
            'number': number,
            'zip': _zip,
            'city': city}
        if save:
            self.save()

    def remove_address(self, save=True):
        del self._data['address']
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

    def update_telephone(self, new, save=True):
        """ Sets @new as telephone number. """
        self._data['telephone'] = new
        if save:
            self.save()

    def update_email(self, new, save=True):
        """ Sets @new as e-mail address. """
        self._data['email'] = new
        if save:
            self.save()

    def update_visibility_preference(self, key, value, save=True):
        """ Update a single visibility preference """

        if 'preferences' not in self._data:
            self._data['preferences'] = {}
        preferences = self._data['preferences']

        if ('visibility' not in preferences
                or isinstance(preferences['visibility'], list)):
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
    def photo_size(self):
        if not self.name:
            return None
        path = os.path.join(settings.SMOELEN_PHOTOS_PATH, str(self.name))

        if not default_storage.exists(path + '.jpg'):
            return None
        img = PIL.Image.open(default_storage.open(path + '.jpg'))
        width, height = img.size
        if default_storage.exists(path + '.orig'):
            # smoel was created using newer strategy. Shrink until it fits the
            # requirements.
            width, height = resize_proportional(img.size[0], img.size[1],
                                                settings.SMOELEN_WIDTH,
                                                settings.SMOELEN_HEIGHT)
        elif width > settings.SMOELEN_WIDTH:
            # smoel was created as high-resolution image, probably 600px wide
            width /= 2
            height /= 2
        else:
            # smoel was created as normal image, probably 300px wide
            pass

        return width, height

    canonical_full_email: typing.Optional[str]
    @property
    def canonical_full_email(self):
        """ Returns the string

                "[human name]" <[canonical e-mail]>
            """
        addr = self.canonical_email
        if not addr:
            return None
        return email.utils.formataddr((six.text_type(self.humanName), addr))

    canonical_email: typing.Optional[str]
    @property
    def canonical_email(self):
        if self.type in ('institute', 'study', 'brand', 'tag'):
            return None
        name = str(self.name if self.name else self.id)
        return "%s@%s" % (name, settings.MAILDOMAIN)

    got_mailman_list: bool
    @property
    def got_mailman_list(self):
        if 'use_mailman_list' in self._data:
            return self._data['use_mailman_list']
        elif 'virtual' in self._data and \
                'type' in self._data['virtual']:
            if self._data['virtual']['type'] == 'sofa':
                return False
        return True

    got_unix_group: bool
    @property
    def got_unix_group(self):
        if 'has_unix_group' in self._data:
            return self._data['has_unix_group']
        else:
            return True

    def add_note(self, what: str, by: Optional['Entity'] = None) -> 'Note':
        dt = now()
        note = Note({'note': what,
                     'on': self._id,
                     'by': None if by is None else _id(by),
                     'at': dt})
        note.save()
        return note

    def get_notes(self) -> Iterator['Note']:
        for d in ncol.find({'on': self._id}, sort=[('at', 1)]):
            yield Note(d)

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
    db_typename: typing.ClassVar[str] = "group"

    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('group-by-name', (),
                    {'name': self.name})
        return ('group-by-id', (), {'_id': self.id})

    def get_current_and_old_members(self) -> \
        typing.Tuple[typing.Set[Entity], typing.Set[Entity]]:
        dt = now()
        cur, _all = set(), set()
        for rel in self.get_rrelated(how=None, deref=set(("how", "who"))):
            _all.add(rel['who'])
            if ((rel['until'] is None or rel['until'] >= dt) and
                    (rel['from'] is None or rel['from'] <= dt)):
                cur.add(rel['who'])
        return (cur, _all - cur)

    def get_members(self) -> typing.List[Entity]:
        dt = now()
        return [r['who'] for r in self.get_rrelated(
                how=None, _from=dt, until=dt, deref=set(("who",)))]

    is_virtual: bool
    @property
    def is_virtual(self):
        return 'virtual' in self._data


class User(Entity):
    db_typename: typing.ClassVar[str] = "user"

    class _Meta(object):
        """ Django expects a user object to have a _meta instance.
            This class is used to emulate it. """

        class _PK(object):
            def __init__(self, user):
                self.__user = user

            def value_to_string(self, obj):
                assert obj is self.__user
                # Due to a regression in new Django, their session framework
                # expects an integer as identifier.  So we just convert our
                # _id hexstring to an integer.  See also kn.leden.auth.
                return int(str(self.__user._id), 16)

        def __init__(self, user):
            self.__user = user
            self.pk = User._Meta._PK(user)

    address = son_property(('address',))
    telephone = son_property(('telephone',))
    email = son_property(('email',))
    pk = son_property(('_id'),)  # primary key for Django

    def __init__(self, data: Dict[str, typing.Any]) -> None:
        super(User, self).__init__(data)
        self._primary_study = -1
        self._meta = User._Meta(self)

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

    def set_preferred_language(self, code, save=True):
        self._data['preferred_language'] = code
        if save:
            if '_id' in self._data:
                ecol.update(
                    {'_id': self._id},
                    {'$set': {'preferred_language': self.preferred_language}}
                )
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
        # XXX: this is a different type
        return self.full_name

    def set_humanName(self):
        raise NotImplemented('setting humanName for users is not implemented')

    password: Optional[bytes]
    @property
    def password(self) -> Optional[bytes]:
        return self._data.get('password', None)

    is_active: bool
    @property
    def is_active(self) -> bool:
        return self._data.get('is_active', True)

    def is_authenticated(self) -> bool:
        # required by django's auth
        return True
    # Required by Django's auth. framework

    def get_username(self):
        # implements Django's User object
        return str(self.name)

    def may_upload_smoel_for(self, user):
        return self == user or \
            'secretariaat' in self.cached_groups_names or \
            'bestuur' in self.cached_groups_names

    full_name: str
    @property
    def full_name(self) -> str:
        if ('person' not in self._data or
                'family' not in self._data['person'] or
                'nick' not in self._data['person']):
            return six.text_type(super(User, self).humanName)
        bits = self._data['person']['family'].split(',', 1)
        if len(bits) == 1:
            return self._data['person']['nick'] + ' ' \
                + self._data['person']['family']
        return self._data['person']['nick'] + bits[1] + ' ' + bits[0]

    first_name: str
    @property
    def first_name(self) -> str:
        return self._data.get('person', {}).get('nick')

    last_name: str
    @property
    def last_name(self) -> str:
        return self._data.get('person', {}).get('family')

    preferred_language: str
    @property
    def preferred_language(self) -> str:
        return self._data.get('preferred_language', settings.LANGUAGE_CODE)

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
        # TODO: will crash if study does not exist
        if self._primary_study == -1:
            self._primary_study = (
                None if not self._data.get('studies', ())
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
        return max([DT_MIN] +
                   [s['until'] for s in self._data.get('studies', ())])

    def study_start(self, study, institute, number, start_date, save=True):
        start_date = datetime.datetime(start_date.year, start_date.month,
                                       start_date.day)
        if 'studies' not in self._data:
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
            raise ValueError(_('studie index bestaat niet'))
        study = studies[index]
        if study['until'] != DT_MAX:
            raise ValueError(_('studie is al beeindigt'))
        if study['from'] >= end_date:
            raise EntityException(_('einddatum voor begindatum'))
        study['until'] = end_date
        if save:
            self.save()

    @property
    def studentNumber(self):
        study = self.proper_primary_study
        return study['number'] if self.proper_primary_study else None

    dateOfBirth: datetime.datetime
    @property
    def dateOfBirth(self):
        return self._data.get('person', {}).get('dateOfBirth')

    def set_dateOfBirth(self, dateOfBirth, save=True):
        if 'person' not in self._data:
            self._data['person'] = {}
        self._data['person']['dateOfBirth'] = dateOfBirth
        if 'is_underage' in self._data:
            del self._data['is_underage']
        if save:
            self.save()

    def remove_dateOfBirth(self, save=True):
        """ Remove date of birth property """

        person = self._data.get('person', {})
        if 'dateOfBirth' in person:
            self._data['is_underage'] = self.is_underage
            person['dateOfBirth'] = None
            if save:
                self.save()

    age: int
    @property
    def age(self):
        # age is a little difficult to calculate because of leap years
        # see http://stackoverflow.com/a/9754466
        today = datetime.date.today()
        date = self.dateOfBirth
        if not date:
            return None
        return (today.year - date.year
                - ((today.month, today.day) < (date.month, date.day)))

    is_underage: bool
    @property
    def is_underage(self):
        ''' Return True, False, or None (if unknown). '''
        if self.age is not None:
            return self.age < 18
        return self._data.get('is_underage', None)

    got_unix_user: bool
    @property
    def got_unix_user(self):
        if 'has_unix_user' in self._data:
            return self._data['has_unix_user']
        else:
            return True

    @property
    def preferences(self):
        return self._data.get('preferences', {})

    @property
    def visibility(self):
        return self.preferences.get('visibility', {})


def set_locale_on_logon(sender, request, user, **kwargs):
    request.session['_language'] = user.preferred_language


user_logged_in.connect(set_locale_on_logon)


class Tag(Entity):
    db_typename: typing.ClassVar[str] = "tag"

    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('tag-by-name', (),
                    {'name': self.name})
        return ('tag-by-id', (), {'_id': self.id})

    def get_bearers(self) -> typing.List[Entity]:
        return [entity(m) for m in ecol.find({
                'tags': self._id})]


class Study(Entity):
    db_typename: typing.ClassVar[str] = "study"

    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('study-by-name', (),
                    {'name': self.name})
        return ('study-by-id', (), {'_id': self.id})


class Institute(Entity):
    db_typename: typing.ClassVar[str] = "institute"

    @permalink
    def get_absolute_url(self):
        if self.name:
            return ('institute-by-name', (),
                    {'name': self.name})
        return ('institute-by-id', (), {'_id': self.id})


class Brand(Entity):
    db_typename: typing.ClassVar[str] = "brand"

    @permalink
    def get_absolute_url(self) -> Tuple[str, Any, Dict[str, EntityID]]:
        if self.name:
            return ('brand-by-name', (),
                    {'name': self.name})
        return ('brand-by-id', (), {'_id': self.id})

    @property
    def sofa_suffix(self) -> str:
        return self._data.get('sofa_suffix', None)


class Note(SONWrapper):
    """ Notes set on an entity as a todo for the secretary or webcie """
    @classmethod
    def by_id(cls, the_id: EntityID) -> Optional["Note"]:
        tmp = ncol.find_one({'_id': the_id})
        return None if tmp is None else Note(tmp)
    @classmethod
    def all(cls) -> Iterable["Note"]:
       return CursorMapper(ncol.find({}, sort=[('at', 1)]), Note)

    at: datetime.datetime
    at = son_property(('at',))
    note: str
    note = son_property(('note',))
    by_id: EntityID
    by_id = son_property(('by',))
    on_id: EntityID
    on_id = son_property(('on',))

    def __init__(self, data: Dict[str, typing.Any]) -> None:
        # todo: typecheck data
        super(Note, self).__init__(data, ncol)

    id: EntityID
    @property
    def id(self) -> str:
        return str(_id(self))

    on: Entity
    @property
    def on(self) -> Optional[Entity]:
        return by_id(self._data['on'])

    by: Optional[Entity]
    @property
    def by(self) -> Optional[Entity]:
        return by_id(self._data['by'])

    messageId: str
    @property
    def messageId(self) -> str:
        return '<note/%s@%s>' % (self.id, settings.MAILDOMAIN)


class InformacieNotification(SONWrapper):

    def __init__(self, data: Dict[str, typing.Any]) -> None:
        super(InformacieNotification, self).__init__(data, incol)

    def user(self) -> User:
        # XXX: typechecker is right to complain
        return typing.cast(User, by_id(self._data['user']))

    def relation(self):
        return relation_by_id(self._data['relation'])

    def tag(self) -> typing.Optional[Tag]:
        return typing.cast(typing.Optional[Tag], by_id(self._data['tag']))

    def entity(self) -> typing.Optional[Entity]:
        return by_id(self._data['entity'])

    def fotoEvent(self):
        import kn.fotos.entities as fEs
        return fEs.by_id(self._data['fotoEvent'])

    def fotoAlbum(self):
        import kn.fotos.entities as fEs
        return fEs.by_id(self._data['fotoAlbum'])

    event = son_property(('event', ))
    when: datetime.datetime
    when = son_property(('when', ))


# List of type of entities
# ######################################################################
TYPE_MAP: Dict[str, typing.Callable[..., Entity]]
TYPE_MAP = {
    'group': Group,
    'user': User,
    'study': Study,
    'institute': Institute,
    'tag': Tag,
    'brand': Brand
}

# vim: et:sta:bs=2:sw=4:
