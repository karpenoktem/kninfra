# vim: et:sta:bs=2:sw=4:
import functools

from django.db.models import permalink
from django.contrib.auth.models import get_hexdigest

from kn.leden.date import now
from kn.leden.mongo import db, SONWrapper, _id
from kn.settings import DT_MIN, DT_MAX, MAILDOMAIN
from kn.base._random import pseudo_randstr

# The collections
# ######################################################################
ecol = db['entities']   # entities: users, group, tags, studies, ...
rcol = db['relations']  # relations: "giedo is chairman of bestuur from
            #             date A until date B"
mcol = db['messages']   # message: used for old code
ncol = db['notes']      # notes on entities by the secretaris

def ensure_indices():
    """ Ensures that the indices we need on the collections are set """
    # entities
	ecol.ensure_index('names', unique=True, sparse=True)
	ecol.ensure_index('types')
	ecol.ensure_index('tags', sparse=True)
	ecol.ensure_index('humanNames.human')
    # relations
	rcol.ensure_index('how', sparse=True)
	rcol.ensure_index('with')
	rcol.ensure_index('who')
	rcol.ensure_index('tags', spare=True)
	rcol.ensure_index([('until',1),
			   ('from',-1)])
	# messages
    mcol.ensure_index('entity')
    # notes
    ncol.ensure_index('on')


# Basic functions to work with entities
# ######################################################################
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
        ret = ecol.find_one({'names': n}, {'names':1})['_id']
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
	return entity(ecol.find_one({'_id': _id(n)}))

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

# Specialized functions to work with entities.
# ######################################################################
def bearers_by_tag_id(tag_id, _as=entity):
    """ Find the bearers of the tag with @tag_id """
    return map(_as, ecol.find({'tags': tag_id}))

def date_to_year(dt):
    """ Returns the `verenigingsjaar' at the date """
    year =  dt.year - 2004
    if dt.month >= 9:
        year += 1
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
    return 'secretariaat' in user.cached_groups_names

def end_relation(__id):
    dt = now()
    rcol.update({'_id': _id(__id)}, {'$set': {'until': dt}})

def add_relation(who, _with, how=None, _from=None, until=None):
    if _from is None:
        _from = DT_MIN
    if until is None:
        until = DT_MAX
    rcol.insert({'who': _id(who),
             'with': _id(_with),
             'how': None if how is None else _id(how),
             'from': _from,
             'until': until})

def disj_query_relations(queries, deref_who=False, deref_with=False,
        deref_how=False):
    """ Find relations matching any one of @queries.
        See @query_relations. """
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
        if query['from'] == DT_MIN and query['until'] == DT_MAX:
            del query['from']
            del query['until']
            bits.append(query)
        elif query['from'] == query['until']:
            query['from'] = {'$lte': query['from']}
            query['until'] = {'$gte': query['until']}
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
    cursor = rcol.find({'$or': bits})
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

def relation_cmp_until(x, y):
    return cmp(DT_MAX if x['until'] is None else x['until'],
           DT_MAX if y['until'] is None else y['until'])

def relation_cmp_from(x, y):
    return cmp(DT_MIN if x['from'] is None else x['from'],
           DT_MIN if y['from'] is None else y['from'])

def remove_relation(who, _with, how,  _from, until):
    if _from is None: _from = DT_MIN
    if until is None: until = DT_MAX
    rcol.remove({'who': _id(who),
             'with': _id(_with),
             'how': None if how is None else _id(how),
             'from': _from,
             'until': until})

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
        if not hasattr(self, '__groups_cache'):
            dt = now()
            self.__groups_cache = [rel['with']
                for rel in self.get_related(
                    None, dt, dt, False, True, False)]
        return self.__groups_cache

    @property
    def cached_groups_names(self):
        if not hasattr(self, '__groups_names_cache'):
            self.__groups_names_cache = set()
            for g in self.cached_groups:
                self.__groups_names_cache.update([
                    str(n) for n in g.names])
        return self.__groups_names_cache

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
		return "<Entity %s (%s)>" % (self.id, self.type)

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

    @property
    def canonical_email(self):
        if self.type in ('institute', 'study', 'brand', 'tag'):
            return None
        return "%s@%s" % (self.name, MAILDOMAIN)

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
              'by': None if by is None else _id(by),
              'at': dt}).save()
    def get_notes(self):
        ds = ncol.find({'on': self._id})
        lut = by_ids([d['by'] for d in ds if d['by'] is not None])
        lut[None] = None
        for d in ncol.find({'on': self._id}):
            yield Note(d, lut[d['by']])

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
                    rel['from'] is None
                    or rel['from'] <= dt):
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
        self._primary_study = None
	@permalink
	def get_absolute_url(self):
		if self.name:
			return ('user-by-name', (),
					{'name': self.name})
		return ('user-by-id', (), {'_id': self.id})
    def set_password(self, pwd, save=True):
        salt = pseudo_randstr()
        alg = 'sha1'
        self._data['password'] = {
                'algorithm': alg,
                'salt': salt,
                'hash': get_hexdigest(alg, salt, pwd)}
        if save:
            self.save()
	def check_password(self, pwd):
        if self.password is None:
            return False
		dg = get_hexdigest(self.password['algorithm'],
				   self.password['salt'], pwd)
		return dg == self.password['hash']
	@property
	def humanName(self):
		return self.full_name
	@property
	def password(self):
		return self._data.get('password', None)
	@property
	def is_active(self):
		return self._data['is_active']
	def is_authenticated(self):
		# required by django's auth
		return True
	def push_message(self, msg):
		mcol.insert({'entity': self._id,
			     'data': msg})
	def pop_messages(self):
		msgs = list(mcol.find({'entity': self._id}))
		mcol.remove({'_id': {'$in': [m['_id'] for m in msgs]}})
		return [m['data'] for m in msgs]
	get_and_delete_messages = pop_messages
	@property
	def primary_email(self):
		# the primary email address is always the first one;
		# we ignore the until field.
		if len(self._data['emailAddresses'])==0:
			return None
		return self._data['emailAddresses'][0]['email']
	@property
	def full_name(self):
		bits = self._data['person']['family'].split(',', 1)
		if len(bits) == 1:
			return self._data['person']['nick'] + ' ' \
					+ self._data['person']['family']
		return self._data['person']['nick'] + bits[1] + ' ' + bits[0]
	@property
	def first_name(self):
		return self._data['person']['nick']
	@property
	def last_name(self):
		return self._data['person']['family']
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
        if self._primary_study==None:
            self._primary_study = None \
                if len(self._data['studies'])==0 \
                else by_id(self._data['studies'][0]['study'])\
                            .as_study()
        return self._primary_study
    @property
    def dateOfBirth(self):
        return self._data.get('person',{}).get('dateOfBirth')
    @property
    def got_unix_user(self):
        if 'has_unix_user' in self._data:
            return self._data['has_unix_user']
        else:
            return True

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
    def __init__(self, data, prefetched_by=None):
        super(Note, self).__init__(data, ncol)
        self._cached_by = prefetched_by
    @property
    def at(self):
        return self._data['at']
    @property
    def note(self):
        return self._data['note']
    @property
    def by_id(self):
        return self._data['by']
    @property
    def by(self):
        if self._cached_by is not None:
            return self._cached_by
        if self._data['by'] is None:
            return None
        return by_id(self._data['by'])


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