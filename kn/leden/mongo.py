import pymongo

from django.conf import settings
from django.utils import six
import typing
from typing import Optional, TypeVar, Any, Union, Mapping

try:
    from pymongo.objectid import ObjectId
except ImportError:
    from bson import ObjectId


conn = pymongo.MongoClient(settings.MONGO_HOST)
db = conn[settings.MONGO_DB]


class RaceCondition(Exception):
    pass


def _id(obj: typing.Union[ObjectId, str, typing.Any]) -> ObjectId:
    if isinstance(obj, ObjectId):
        return obj
    if isinstance(obj, str):
        return ObjectId(obj)
    elif isinstance(obj, six.string_types):
        return ObjectId(obj)
    elif hasattr(obj, '_id'):
        return obj._id
    raise ValueError("Don't know how to turn {!r} into an _id".format(obj))


class SONWrapper(object):

    def __init__(self, data: Mapping[str, Any], collection: Any, parent: Optional["SONWrapper"]=None, detect_race: bool=False) -> None:
        '''
            parent:      SONWrapper can be nested. This is the parent.
            detect_race: Add a _version field which is incremented with each
                         update to detect (and fail on) race conditions.
        '''
        self._data = data
        self._collection = collection
        self._parent = parent
        self._detect_race = detect_race

    def delete(self) -> None:
        assert self._data['_id'] is not None
        # TODO check version
        # XXX: remove is deprecated
        self._collection.remove({
            '_id': self._data['_id']})
    # We take the keyword argument update_fields to be compatible with
    # Django's Model.save.  However, we do not use it, yet.

    def save(self, update_fields: None=NotImplemented) -> None:
        if self._parent is None:
            if '_id' in self._data:
                if self._detect_race:
                    self._data['_version'] += 1
                    result = self._collection.update(
                        {'_id': self._data['_id'],
                         '_version': self._data['_version'] - 1},
                        self._data,
                        w=1
                    )
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
    def _id(self) -> ObjectId:
        if self._parent is None:
            return self._data['_id']
        return self._parent._id

    @property
    def _version(self) -> int:
        if self._parent is None:
            return int(self._data['_version'])
        return int(self._parent._version)

    def __repr__(self) -> str:
        return "<SONWrapper for %s>" % self._id

T = typing.TypeVar('T')
def son_property(path: typing.Sequence[str], default: Optional[T]=None) -> property:
    """ A convenience shortcut to create properties on SONWrapper
        subclasses.  Will return a getter/setter property that
        gets/sets self._data[path[0]]...[path[-1]] verbatim. """

    def __getter(self: SONWrapper) -> Optional[T]:
        obj = self._data
        for bit in path[:-1]:
            obj = obj.get(bit, {})
        return obj.get(path[-1], default)

    def __setter(self: SONWrapper, x: T) -> None:
        obj = self._data
        for bit in path[:-1]:
            if bit not in obj:
                obj[bit] = {}
            obj = obj[bit]
        obj[path[-1]] = x
    return property(__getter, __setter)

# vim: et:sta:bs=2:sw=4:
