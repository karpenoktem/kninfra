import functools

from django.db.models import permalink
from django.contrib.auth.models import get_hexdigest

from kn.leden.date import now
from kn.leden.mongo import db, SONWrapper, _id
from kn.settings import DT_MIN, DT_MAX, MAILDOMAIN

# The collections
# ###################################################################### 
ecol = db['entities']   # entities: users, group, tags, studies, ...
rcol = db['relations']  # relations: "giedo is chairman of bestuur from
                        #             date A until date B"
mcol = db['messages']   # message: used for old code

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

def ids_by_names(ns):
        """ Finds _ids of entities by a list of names """
        ret = {}
        nss = frozenset(ns)
        for m in ecol.find({'names': {'$in': ns}}, {'names':1}):
                for n in m['names']:
                        if n in nss:
                                ret[n] = m['_id']
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
                        #      mongo will not use its indeces.
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

def relation_cmp_until(x, y):
        return cmp(DT_MAX if x['until'] is None else x['until'],
                   DT_MAX if y['until'] is None else y['until'])

def relation_cmp_from(x, y):
        return cmp(DT_MIN if x['from'] is None else x['from'],
                   DT_MIN if y['from'] is None else y['from'])



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
                return rcol.exists({'who': _id(self),
                                    'how': _id(how),
                                    'with': _id(whom)})

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
                nm = self._data.get('names', (None,))[0]
                return nm if nm is None else EntityName(self, nm)
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

	def as_user(self): return User(self._data)
	def as_group(self): return Group(self._data)
	def as_brand(self): return Brand(self._data)
	def as_tag(self): return Tag(self._data)
	def as_study(self): return Study(self._data)
	def as_institute(self): return Institute(self._data)

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

class Group(Entity):
	@permalink
	def get_absolute_url(self):
		if self.name:
			return ('group-by-name', (),
					{'name': self.name})
		return ('group-by-id', (), {'_id': self.id})
        def get_members(self):
                dt = now()
                return [r['who'] for r in self.get_rrelated(
                                how=None, _from=dt, until=dt)]
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
	def check_password(self, pwd):
		dg = get_hexdigest(self.password['algorithm'],
				   self.password['salt'], pwd)
		return dg == self.password['hash']
	@property
	def humanName(self):
		return self.full_name
	@property
	def password(self):
		return self._data['password']
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
        def primary_study(self):
                if self._primary_study==None:
                        self._primary_study = None \
                                if len(self._data['studies'])==0 \
                                else by_id(self._data['studies'][0]['study'])\
                                                        .as_study()
                return self._primary_study
class Tag(Entity):
	@permalink
	def get_absolute_url(self):
		if self.name:
			return ('tag-by-name', (),
					{'name': self.name})
		return ('tag-by-id', (), {'_id': self.id})
	def get_bearers(self):
		return [entity(m) for m in ecol.find({
				'tags': self._id}).sort(
						'humanNames.human')]

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
