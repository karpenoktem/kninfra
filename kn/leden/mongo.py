import pymongo
from pymongo.objectid import ObjectId
from kn.settings import MONGO_DB, MONGO_HOST

conn = pymongo.Connection(MONGO_HOST)
db = conn[MONGO_DB]

def _id(obj):
        if isinstance(obj, ObjectId):
                return obj
	if isinstance(obj, basestring):
		return ObjectId(obj)
        if hasattr(obj, '_id'):
                return obj._id
        raise ValueError

class SONWrapper(object):
	def __init__(self, data, collection, parent=None):
		self._data = data
		self._collection = collection
		self._parent = parent
	def save(self):
		if self._parent is None:
                        if '_id' in self._data:
                                self._collection.update({
                                        '_id': self._data['id']}, self._data)
                        else:
                                self._data['_id'] = self._collection.insert(
                                                self._data)
		else:
			self._parent.save()
	@property
	def _id(self):
		if self._parent is None:
			return self._data['_id']
		return self._parent._id
	def __repr__(self):
		return "<SONWrapper for %s>" % self._id

