import functools

from django.db.models import permalink
from django.contrib.auth.models import get_hexdigest
from pymongo.objectid import ObjectId

from kn.leden.mongo import db
from kn.settings import DT_MIN, DT_MAX

ecol = db['entities']
mcol = db['messages']

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
	def get_rrelated(self):
		how_ids = list()
		h_lut = dict()
		rrelated = list()
		for m in ecol.find({'relations.with': self.data['_id']}):
			for n in m['relations']:
				if n['with'] != self.data['_id']:
					continue
				n = dict(n)
				if n['how']:
					how_ids.append(n['how'])
				if n['from'] == DT_MIN:
					n['from'] = None
				if n['until'] == DT_MAX:
					n['until'] = None
				n['who'] = entity(m)
				rrelated.append(n)
		for m in ecol.find({'_id': {'$in': how_ids}}):
			h_lut[m['_id']] = entity(m)
		for m in rrelated:
			m['how'] = h_lut.get(m['how'])
		return rrelated

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
			rel = dict(rel)
			rel['how'] = e_lut.get(rel['how'])
			rel['with'] = e_lut.get(rel['with'])
			if rel['from'] == DT_MIN:
				rel['from'] = None
			if rel['until'] == DT_MAX:
				rel['until'] = None
			yield rel
	
	def get_tags(self):
		for m in ecol.find({'_id': {'$in': self.data['tags']}}
				).sort('humanNames.human', 1):
			yield Tag(m)

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
	@property
	def humanName(self):
		return self.data['humanNames'][0]['human']
	@property
	def genitive_prefix(self):
		return self.data['humanNames'][0]['genitive_prefix']
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
	def humanName(self):
		return self.full_name
	@property
	def password(self):
		return self.data['password']
	@property
	def is_active(self):
		return self.data['is_active']
	def is_authenticated(self):
		# required by django's auth
		return True
	def push_message(self, msg):
		mcol.insert({'entity': self.data['_id'],
			     'data': msg})
	def pop_messages(self):
		msgs = list(mcol.find({'entity': self.data['_id']}))
		mcol.remove({'_id': {'$in': [m['_id'] for m in msgs]}})
		return [m['data'] for m in msgs]
	get_and_delete_messages = pop_messages
	@property
	def primary_email(self):
		return self.data['emails'][0]
	@property
	def full_name(self):
		bits = self.data['person']['family'].split(',', 1)
		if len(bits) == 1:
			return self.data['person']['nick'] + ' ' \
					+ self.data['person']['family']
		return self.data['person']['nick'] + bits[1] + ' ' + bits[0]
class Tag(Entity):
	def get_bearers(self):
		return [entity(m) for m in ecol.find({
				'tags': self.data['_id']}).sort(
						'humanNames.human')]

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
	ecol.ensure_index('tags')
	ecol.ensure_index('relations.how')
	ecol.ensure_index('relations.with')
	ecol.ensure_index([('relations.until',1),
			   ('relations.from',-1)])
	ecol.ensure_index('humanNames.human')
	mcol.ensure_index('entity')
