import functools

from django.db.models import permalink
from django.contrib.auth.models import get_hexdigest

from kn.leden.mongo import db, SONWrapper, _id
from kn.settings import DT_MIN, DT_MAX

ecol = db['entities']
mcol = db['messages']
rcol = db['relations']

def entity(d):
	if d is None:
		return None
	return TYPE_MAP[d['types'][0]](d)

def by_name(n):
	return entity(ecol.find_one({'names': n}))

def by_id(n):
	return entity(ecol.find_one({'_id': _id(n)}))

def all():
	for m in ecol.find():
		yield entity(m)

class EntityName(object):
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
	def __init__(self, data):
		super(Entity, self).__init__(data, ecol)
        def is_related_with(self, whom, how=None):
                return rcol.exists({'who': _id(self),
                                    'how': _id(how),
                                    'with': _id(whom)})
	def get_rrelated(self):
		rel_ids = list()
		e_lut = dict()
		rels = list(rcol.find({'with': self._id}))
		for rel in rels:
			rel_ids.append(rel['who'])
			if rel['how']:
				rel_ids.append(rel['how'])
		for m in ecol.find({'_id': {'$in': rel_ids}}):
			e_lut[m['_id']] = entity(m)
		for rel in rels:
			rel['with'] = self
			rel['how'] = e_lut.get(rel['how'])
			rel['who'] = e_lut.get(rel['who'])
			if rel['from'] == DT_MIN:
				rel['from'] = None
			if rel['until'] == DT_MAX:
				rel['until'] = None
			yield rel

	def get_related(self):
		rel_ids = list()
		e_lut = dict()
		rels = list(rcol.find({'who': self._id}))
		for rel in rels:
			rel_ids.append(rel['with'])
			if rel['how']:
				rel_ids.append(rel['how'])
		for m in ecol.find({'_id': {'$in': rel_ids}}):
			e_lut[m['_id']] = entity(m)
		for rel in rels:
			rel['who'] = self
			rel['how'] = e_lut.get(rel['how'])
			rel['with'] = e_lut.get(rel['with'])
			if rel['from'] == DT_MIN:
				rel['from'] = None
			if rel['until'] == DT_MAX:
				rel['until'] = None
			yield rel
	
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
		try:
			return next(self.names)
		except StopIteration:
			return None
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
	def as_sofa(self): return Sofa(self._data)
	def as_brand(self): return Brand(self._data)
	def as_tag(self): return Tag(self._data)
	def as_study(self): return Study(self._data)
	def as_institute(self): return Institute(self._data)

class Group(Entity):
	@permalink
	def get_absolute_url(self):
		if self.name:
			return ('group-by-name', (),
					{'name': self.name})
		return ('group-by-id', (), {'_id': self.id})
class User(Entity):
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
class Sofa(Entity):
	@permalink
	def get_absolute_url(self):
		if self.name:
			return ('sofa-by-name', (),
					{'name': self.name})
		return ('sofa-by-id', (), {'_id': self.id})
class Brand(Entity):
        @permalink
        def get_absolute_url(self):
                if self.name:
                        return ('brand-by-name', (),
                                        {'name': self.name})
                return ('brand-by-id', (), {'_id': self.id})

def relation_cmp_until(x, y):
        return cmp(DT_MAX if x['until'] is None else x['until'],
                   DT_MAX if y['until'] is None else y['until'])
def relation_cmp_from(x, y):
        return cmp(DT_MIN if x['from'] is None else x['from'],
                   DT_MIN if y['from'] is None else y['from'])

TYPE_MAP = {
	'group': Group,
	'user': User,
	'study': Study,
	'institute': Institute,
	'tag': Tag,
	'sofa': Sofa,
	'brand': Brand
}

def of_type(t):
	for m in ecol.find({'types': t}):
		yield TYPE_MAP[t](m)

groups = functools.partial(of_type, 'group')
users = functools.partial(of_type, 'user')
studies = functools.partial(of_type, 'study')
institutes = functools.partial(of_type, 'institute')
tags = functools.partial(of_type, 'tag')
sofas = functools.partial(of_type, 'sofa')
brands = functools.partial(of_type, 'brand')

def ensure_indices():
	ecol.ensure_index('names', unique=True, sparse=True)
	ecol.ensure_index('types')
	ecol.ensure_index('tags', sparse=True)
	rcol.ensure_index('how', sparse=True)
	rcol.ensure_index('with')
	rcol.ensure_index('who')
	rcol.ensure_index('tags', spare=True)
	rcol.ensure_index([('until',1),
			   ('from',-1)])
	ecol.ensure_index('humanNames.human')
	mcol.ensure_index('entity')
