from kn.leden.mongo import db, SONWrapper, _id, son_property
from kn import settings

from django.db.models import permalink

import os
import re
import Image
import random
import os.path
import mimetypes
import subprocess
from collections import namedtuple


cache_tuple = namedtuple('cache_tuple', ('ext', 'mimetype'))

fcol = db['fotos']
lcol = db['fotoLocks']


def ensure_indices():
    fcol.ensure_index([('type', 1), ('oldId', 1)], sparse=True)
    fcol.ensure_index([('path', 1), ('name', 1)])
    fcol.ensure_index([('type', 1), ('path', 1),
                       ('random', 1), ('visibility', 1)])
    fcol.ensure_index('tags', sparse=True)
    fcol.ensure_index([('caches', 1), ('type', 1)], sparse=True)
    fcol.ensure_index([('path', 1), ('visibility', 1), ('name', 1)])

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
        name = bits[0]
        pp = '' if name else None
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
    title = son_property(('title',))
    orientation = son_property(('orientation',), 0)

    description = son_property(('description',))
    visibility = son_property(('visibility',))

    def required_visibility(self, user):
        if user is None:
            return frozenset(('world',))
        if user == 'system' or 'webcie' in user.cached_groups_names:
            return frozenset(('leden', 'world', 'hidden'))
        if 'leden' in user.cached_groups_names:
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

    # NOTE keep up to date with media/fotos.js
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

    def get_cache_meta(self, cache):
        return self._data.get('cacheMeta', {}).get(cache, {})

    def get_cache_path(self, cache):
        if cache == 'full':
            return os.path.join(settings.PHOTOS_DIR, self.path, self.name)
        path = os.path.join(settings.PHOTOS_CACHE_DIR, cache,
                            self.path, self.name)
        ext = self.CACHES[cache].ext
        if ext:
            path += '.' + ext
        return path

    def get_cache_mimetype(self, cache):
        mimetype = self.CACHES[cache].mimetype
        if mimetype is not None:
            return mimetype
        return mimetypes.guess_type(self.get_cache_path(cache))[0]

    def ensure_cached(self, cache):
        if not cache in self.CACHES:
            raise KeyError
        if cache in self.caches:
            return True
        if not self.lock_cache(cache):
            return False
        try:
            meta = self._cache(cache)
            if meta is None:
                return False
            # Normally, we would just modify _data and .save().  However,
            # as the _cache operation may take quite some time, a full
            # .save() might overwrite other changes. (Like other caches.)
            # Thus we perform the change manually.
            if not 'caches' in self._data:
                self._data['caches'] = []
            if not 'cacheMeta' in self._data:
                self._data['cacheMeta'] = {}
            self._data['cacheMeta'][cache] = meta
            self._data['caches'].append(cache)
            fcol.update({'_id': self._id},
                        {'$addToSet': {'caches': cache},
                         '$set': {'cacheMeta.'+cache: meta}})
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

    def list(self, user):
        required_visibility = self.required_visibility(user)
        albums = map(entity, fcol.find({'path': self.full_path,
                           'type': 'album',
                           'visibility': {'$in': tuple(required_visibility)}},
                           ).sort('name', -1))
        fotos = map(entity, fcol.find({'path': self.full_path,
                           'type': {'$ne': 'album'},
                           'visibility': {'$in': tuple(required_visibility)}},
                           ).sort([('created', 1), ('name', 1)]))

        return albums+fotos

    def get_random_foto_for(self, user):
        r = random.random()
        required_visibility = self.required_visibility(user)
        while True:
            import pprint
            pprint.pprint(fcol.find(
                    {'random': {'$lt': r},
                     'path': {'$regex': re.compile(
                                "^%s(/|$)" % re.escape(self.full_path))},
                     'type': 'foto',
                     'visibility': {'$in': tuple(required_visibility)}},
                        sort=[('random',-1)]).explain())
            f = entity(fcol.find_one(
                    {'random': {'$lt': r},
                     'path': {'$regex': re.compile(
                                "^%s(/|$)" % re.escape(self.full_path))},
                     'type': 'foto',
                     'visibility': {'$in': tuple(required_visibility)}},
                        sort=[('random',-1)]))
            if f is not None:
                return f
            if r == 1:
                return None
            r = 1

class Foto(FotoEntity):
    CACHES = {'thumb': cache_tuple('jpg', 'image/jpeg'),
              'thumb2x': cache_tuple('jpg', 'image/jpeg'),
              'large': cache_tuple('jpg', 'image/jpeg'),
              'large2x': cache_tuple('jpg', 'image/jpeg'),
              'full': cache_tuple(None, None),
              }


    def __init__(self, data):
        super(Foto, self).__init__(data)

    def _cache(self, cache):
        if cache == 'full':
            return {}
        source = self.original_path
        target = self.get_cache_path(cache)
        target_dir = os.path.dirname(target)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if cache == 'thumb':
            subprocess.call(['convert',
                             source,
                             '-resize', '200x',
                             '-rotate', str(self.orientation),
                             target])
        elif cache == 'thumb2x':
            subprocess.call(['convert',
                             source,
                             '-resize', '400x',
                             '-rotate', str(self.orientation),
                             target])
        elif cache == 'large':
            subprocess.call(['convert',
                             source,
                             '-resize', '850x',
                             '-rotate', str(self.orientation),
                             target])
        elif cache == 'large2x':
            subprocess.call(['convert',
                             source,
                             '-quality', '90',
                             '-resize', '1700x',
                             '-rotate', str(self.orientation),
                             target])
        # No worries: Image.open is lazy and will only read headers
        return {'size': Image.open(target).size}


class Video(FotoEntity):
    def __init__(self, data):
        super(Video, self).__init__(data)

CACHE_TYPES = (
        'thumb',
        'thumb2x',
        'large',
        'large2x',
        'full',
    )

TYPE_MAP = {
        'album':        FotoAlbum,
        'foto':         Foto,
        'video':        Video
    }

# vim: et:sta:bs=2:sw=4:
