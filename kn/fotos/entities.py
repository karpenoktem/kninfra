from kn.leden.mongo import db, SONWrapper, _id, son_property
from kn import settings

from django.db.models import permalink

import os
import os.path
import subprocess
from collections import namedtuple

cache_tuple = namedtuple('cache_tuple', ('ext', 'mimetype'))

fcol = db['fotos']
lcol = db['fotoLocks']


def ensure_indices():
    fcol.ensure_index([('type', 1), ('oldId', 1)], sparse=True)
    fcol.ensure_index([('path', 1), ('name', 1)])
    fcol.ensure_index([('type', 1), ('parents', 1), ('random', 1)])
    fcol.ensure_index('tags', sparse=True)
    fcol.ensure_index([('cache', 1), ('type', 1)], sparse=True)
    fcol.ensure_index([('path', 1), ('visibility', 1), ('name', 1)])

def path_to_parents(p):
    if not p:
        return []
    parents = []
    cur = None
    for bit in p.split('/'):
        if cur:
            cur += '/' + bit
        else:
            cur = bit
        parents.append(cur)
    return parents

def entity(d):
    if d is None:
        return None
    return TYPE_MAP[d['type']](d)

def by_oldId(_type, oldId):
    return entity(fcol.find_one({'type': _type, 'oldId': oldId}))

def by_path_and_name(p, n):
    return entity(fcol.find_one({'path': p, 'name': n}))

def by_path(p):
    bits = p.rsplit('/', 1)
    if len(bits) == 1:
        pp = ''
        name = bits[0]
    else:
        pp, name = bits
    return by_path_and_name(pp, name)

class FotoEntity(SONWrapper):
    CACHES = {}

    def __init__(self, data):
        super(FotoEntity, self).__init__(data, fcol)

    @property
    def id(self):
        return str(self._data['_id'])

    oldId = son_property(('oldId',))
    name = son_property(('name',))
    path = son_property(('path',))
    _type = son_property(('type',))
    caches = son_property(('caches',), ())

    @property
    def title(self):
        if self._data.get('title'):
            return self._data['title']
        return self._data['name']

    description = son_property(('description',))
    visibility = son_property(('visibility',))

    def required_visibility(self, user):
        if user is None:
            return frozenset(('world',))
        if 'webcie' in user._cached_groups_names:
            return frozenset(('leden', 'world', 'hidden'))
        if 'leden' in user._cached_groups_names:
            return frozenset(('leden', 'world'))
        return frozenset(('world',))

    def may_view(self, user):
        return bool(self.required_visibility(user)
                        & frozenset(self.visibility))

    @permalink
    def get_browse_url(self):
        return ('fotos-browse', (), {'path': self.full_path})

    @property
    def full_path(self):
        if not self.path:
            return self.name
        return self.path + '/' + self.name

    @permalink
    def get_cache_url(self, cache):
        return ('fotos-cache', (), {'path': self.full_path,
                                    'cache': cache})

    @permalink
    def get_thumbnail_url(self):
        return ('fotos-cache', (), {'path': self.full_path,
                                   'cache': 'thumb'})
    @permalink
    def get_thumbnail2x_url(self):
        return ('fotos-cache', (), {'path': self.full_path,
                                   'cache': 'thumb2x'})

    def lock_cache(self, cache):
        ret = lcol.find_and_modify({'_id': self._id},
                                   {'$addToSet': {'cacheLocks': cache}},
                                   upsert=True)
        if ret is None:
            return True
        return cache not in ret.get('cacheLocks', ())

    def unlock_cache(self, cache):
        ret = lcol.update({'_id': self._id},
                          {'$pull': {'cacheLocks': cache}})

    def get_cache_path(self, cache):
        path = os.path.join(settings.PHOTOS_CACHE_DIR, cache,
                            self.path, self.name)
        ext = self.CACHES[cache].ext
        if ext:
            path += '.' + ext
        return path

    def get_cache_mimetype(self, cache):
        return self.CACHES[cache].mimetype

    def ensure_cached(self, cache):
        if not cache in self.CACHES:
            raise KeyError
        if cache in self.caches:
            return True
        if not self.lock_cache(cache):
            return False
        try:
            self._cache(cache)
            # Normally, we would just modify _data and .save().  However,
            # as the _cache operation may take quite some time, a full
            # .save() might overwrite other changes. (Like other caches.)
            # Thus we perform the change manually.
            if not 'caches' in self._data:
                self._data['caches'] = []
            self._data['caches'].append(cache)
            fcol.update({'_id': self._id}, {'$addToSet': {'caches': cache}})
        finally:
            self.unlock_cache(cache)
        return True

    def _cache(self, cache):
        raise NotImplementedError

    @property
    def original_path(self):
        return os.path.join(settings.PHOTOS_DIR, self.path, self.name)

class FotoAlbum(FotoEntity):
    def __init__(self, data):
        super(FotoAlbum, self).__init__(data)

    def list(self, user, offset, count):
        required_visibility = self.required_visibility(user)
        return map(entity, fcol.find({'path': self.full_path,
                           'visibility': {'$in': tuple(required_visibility)}},
                            skip=offset, limit=count
                           ).sort('name', -1))
    
class Foto(FotoEntity):
    CACHES = {'thumb': cache_tuple('jpg', 'image/jpeg'),
              'thumb2x': cache_tuple('jpg', 'image/jpeg'),
              'large': cache_tuple('jpg', 'image/jpeg'),
              'large2x': cache_tuple('jpg', 'image/jpeg'),
              }


    def __init__(self, data):
        super(Foto, self).__init__(data)

    def _cache(self, cache):
        source = self.original_path
        target = self.get_cache_path(cache)
        target_dir = os.path.dirname(target)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if cache == 'thumb':
            subprocess.call(['convert',
                             source,
                             '-resize', '200x',
                             target])
        elif cache == 'thumb2x':
            subprocess.call(['convert',
                             source,
                             '-resize', '400x',
                             target])
        elif cache == 'large':
            subprocess.call(['convert',
                             source,
                             '-resize', '850x',
                             target])
        elif cache == 'large2x':
            subprocess.call(['convert',
                             source,
                             '-quality', '90',
                             '-resize', '1700x',
                             target])
        return True


class Video(FotoEntity):
    def __init__(self, data):
        super(Video, self).__init__(data)

CACHE_TYPES = (
        'thumb',
        'thumb2x',
        'large',
        'large2x',
    )

TYPE_MAP = {
        'album':        FotoAlbum,
        'foto':         Foto,
        'video':        Video
    }

# vim: et:sta:bs=2:sw=4:
