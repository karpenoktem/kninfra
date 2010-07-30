import functools

from kn.leden.mongo import db
from django.contrib.auth.models import get_hexdigest

ecol = db['entities']

def entity(d):
	if d is None:
		return None
	return TYPE_MAP[d['types'][0]](d)

def by_name(n):
	return entity(ecol.find_one({'names': n}))

def by_id(n):
	return entity(ecol.find_one({'_id': n}))

def all():
	for m in ecol.find():
		yield entity(m)

class Entity(object):
	def __init__(self, data=None):
		self.data = data

	@property
	def tags(self):
		for m in ecol.find({'_id': {'$in': self.data['tags']}}):
			yield Tag(m)
	@property
	def names(self):
		for n in self.data['names']:
			yield(n['human'], n['name'])
	def save(self):
		ecol.update({'_id': self.data['_id']},
			    self.data)

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
	def id(self):
		return str(self.data['_id'])
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
