import pymongo

try:
    from pymongo.objectid import ObjectId
except ImportError:
    from bson import ObjectId

from django.conf import settings

conn = pymongo.Connection(settings.MONGO_HOST)
db = conn[settings.MONGO_DB]

class RaceCondition(Exception):
    pass

def _id(obj):
    if isinstance(obj, ObjectId):
        return obj
    if isinstance(obj, basestring):
        return ObjectId(obj)
    if hasattr(obj, '_id'):
        return obj._id
    raise ValueError

class SONWrapper(object):
    def __init__(self, data, collection, parent=None, detect_race=False):
        '''
            parent:      SONWrapper can be nested. This is the parent.
            detect_race: Add a _version field which is incremented with each
                         update to detect (and fail on) race conditions.
        '''
        self._data = data
        self._collection = collection
        self._parent = parent
        self._detect_race = detect_race
    def delete(self):
        assert self._data['_id'] is not None
        # TODO check version
        self._collection.remove({
            '_id': self._data['_id']})
    # We take the keyword argument update_fields to be compatible with
    # Django's Model.save.  However, we do not use it, yet.
    def save(self, update_fields=NotImplemented):
        if self._parent is None:
            if '_id' in self._data:
                if self._detect_race:
                    self._data['_version'] += 1
                    result = self._collection.update({
                        '_id': self._data['_id'],
                        '_version': self._data['_version']-1}, self._data, w=1)
                    if result['n'] < 1:
                        raise RaceCondition('Document was not saved')
                else:
                    self._collection.update({
                        '_id': self._data['_id']}, self._data)
            else:
                if self._detect_race:
                    self._data['_version'] = 1
                self._data['_id'] = self._collection.insert(
                        self._data)
        else:
            self._parent.save()
    @property
    def _id(self):
        if self._parent is None:
            return self._data['_id']
        return self._parent._id
    @property
    def _version(self):
        if self._parent is None:
            return self._data['_version']
        return self._parent._version
    def __repr__(self):
        return "<SONWrapper for %s>" % self._id

def son_property(path, default=None):
    """ A convenience shortcut to create properties on SONWrapper
        subclasses.  Will return a getter/setter property that
        gets/sets self._data[path[0]]...[path[-1]] verbatim. """
    def __getter(self):
        obj = self._data
        for bit in path[:-1]:
            obj = obj.get(bit, {})
        return obj.get(path[-1], default)
    def __setter(self, x):
        obj = self._data
        for bit in path[:-1]:
            if bit not in obj:
                obj[bit] = {}
            obj = obj[bit]
        obj[path[-1]] = x
    return property(__getter, __setter)

# vim: et:sta:bs=2:sw=4:
