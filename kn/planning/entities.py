from kn.leden.mongo import  db, SONWrapper, son_property, _id

import kn.leden.entities as Es

wcol = db['planning_workers']
pcol = db['planning_pools']
vcol = db['planning_vacancies']


# ---
def ensure_indices():
	wcol.ensure_index('user')
	wcol.ensure_index('pools')
	vcol.ensure_index('pool')
	pcol.ensure_index('name')


class Worker(SONWrapper):
	def __init__(self, data):
		super(Worker, self).__init__(data, wcol)
	@classmethod
	def from_data(cls, data):
		if data==None:
			return None
		return cls(data)
	pools = son_property(('pools',))
	user_id = son_property(('user',))

	@classmethod
	def all_in_pool(cls, p):
		for m in wcol.find({'pools':  _id(p)}):
			yield cls.from_data(m)

	def get_user(self):
		return Es.by_id(self.user_id)
	def set_user(self, x):
		self.user_id = _id(x)
	user = property(get_user, set_user)


class Pool(SONWrapper):
	def __init__(self, data):
		super(Pool, self).__init__(data, pcol)
	@classmethod
	def from_data(cls, data):
		if data==None:
			return None
		return cls(data)

	name = son_property(('name',))

	@classmethod
	def all(cls):
		for c in pcol.find():
			yield cls.from_data(c)
	@classmethod
	def by_name(cls, n):
		return cls.from_data(pcol.find_one({'name': n}))

	def vacancies(self):
		return Vacancy.all_in_pool(self)

class Vacancy(SONWrapper):
	formField = None

	def __init__(self, data):
		super(Vacancy, self).__init__(data, vcol)

	@classmethod
	def from_data(cls, data):
		if data==None:
			return None
		return cls(data)

	name = son_property(('name',))
	date = son_property(('date',))
	begin = son_property(('begin',))
	end = son_property(('end',))
	pool_id = son_property(('pool',))
	assignee_id = son_property(('assignee',))

	def get_assignee(self):
		aid = self.assignee_id
		if (aid==None):
			return None
		return Worker.by_id(self.assignee_id)

	def set_assignee(self, value):
		if (value==None):
			self.assignee_id = None
		else:
			self.assignee_id = _id(value)
	assignee = property(get_assignee, set_assignee)

	def set_form_field(self, f):
		self.formField = f

	def get_form_field(self, ):
		return self.formField.__str__()

	@property
	def begin_time(self):
		return self.begin.strftime('%H:%M')

	@property
	def end_time(self):
		return self.end.strftime('%H:%M')

	@classmethod
	def all_in_pool(cls, p):
		for v in vcol.find({'pool': _id(p)}):
			yield cls.from_data(v)


#def by_name(name):
#	d = mcol.find_one({'list': name})
#	return None if d is None else ModerationRecord(d)
