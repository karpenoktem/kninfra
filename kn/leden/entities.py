import functools

from django.db.models import permalink
from django.contrib.auth.models import get_hexdigest
from pymongo.objectid import ObjectId

from kn.leden.mongo import db

ecol = db['entities']

def entity(d):
	if d is None:
		return None
	return TYPE_MAP[d['types'][0]](d)

def by_name(n):
	return entity(ecol.find_one({'names': n}))

def by_id(n):
	if isinstance(n, basestring):
		n = ObjectId(n)
	return entity(ecol.find_one({'_id': n}))

def all():
	for m in ecol.find():
		yield entity(m)

class Entity(object):
	def __init__(self, data=None):
		self.data = data
	def get_related(self):
		rel_ids = list()
		e_lut = dict()
		for rel in self.data['relations']:
			rel_ids.append(rel['with'])
			if rel['how']:
				rel_ids.append(rel['how'])
		for m in ecol.find({'_id': {'$in': rel_ids}}):
			e_lut[m['_id']] = entity(m)
		for rel in self.data['relations']:
			rel['how'] = e_lut.get(rel['how'])
			rel['with'] = e_lut.get(rel['with'])
			yield rel
	@property
	def related_ids(self):
		for x in self.data['relations']:
			yield x['with']
	@property
	def type(self):
		return self.data['types'][0]
	@property
	def id(self):
		return str(self.data['_id'])
	@property
	def tags(self):
		for m in ecol.find({'_id': {'$in': self.data['tags']}}):
			yield Tag(m)
	@property
	def primary_name(self):
		if self.data['names']:
			return self.data['names'][0]
		return None
	@property
	def names(self):
		return self.data['names']
	def save(self):
		ecol.update({'_id': self.data['_id']},
			    self.data)
	@permalink
	def get_absolute_url(self):
		if self.primary_name:
			return ('entity-by-name', (),
					{'name': self.primary_name})
		return ('entity-by-id', (), {'_id': self.id})

	def __repr__(self):
		return "<Entity %s (%s)>" % (self.id, self.type)

	def as_user(self): return User(self.data)
	def as_group(self): return Group(self.data)
	def as_seat(self): return Seat(self.data)
	def as_tag(self): return Tag(self.data)
	def as_study(self): return Study(self.data)
	def as_institute(self): return Institute(self.data)

class Group(Entity):
	pass
class User(Entity):
	def check_password(self, pwd):
		dg = get_hexdigest(self.password['algorithm'],
				   self.password['salt'], pwd)
		return dg == self.password['hash']
	@property
	def password(self):
		return self.data['password']
	@property
	def is_active(self):
		return self.data['is_active']
	def is_authenticated(self):
		# required by django's auth
		return True
	def get_and_delete_messages(self):
		# TODO stub
		return []
	@property
	def full_name(self):
		bits = self.data['person']['family'].split(',', 1)
		if len(bits) == 1:
			return self.data['person']['nick'] + ' ' \
					+ self.data['person']['family']
		return self.data['person']['nick'] + bits[1] + ' ' + bits[0]
class Tag(Entity):
	pass
class Study(Entity):
	pass
class Institute(Entity):
	pass
class Seat(Entity):
	pass

TYPE_MAP = {
	'group': Group,
	'user': User,
	'study': Study,
	'institute': Institute,
	'tag': Tag,
	'seat': Seat
}

def of_type(t):
	for m in ecol.find({'type': t}):
		yield TYPE_MAP[t](m)

groups = functools.partial(of_type, 'group')
users = functools.partial(of_type, 'user')
studies = functools.partial(of_type, 'study')
institutes = functools.partial(of_type, 'institute')
tags = functools.partial(of_type, 'tag')
seats = functools.partial(of_type, 'seat')

def ensure_indices():
	ecol.ensure_index('names', unique=True)
	ecol.ensure_index('types')
	ecol.ensure_index('relations.how')
	ecol.ensure_index('relations.with')
	ecol.ensure_index([('relations.from',1),
			   ('relations.until',-1)])
	ecol.ensure_index('humanNames.human')
