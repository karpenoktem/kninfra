from kn.leden.mongo import db, SONWrapper, _id, son_property
from django.db.models import permalink

fcol = db['fotos']


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
    def __init__(self, data):
        super(FotoEntity, self).__init__(data, fcol)

    @property
    def id(self):
        return str(self._data['_id'])

    oldId = son_property(('oldId',))
    name = son_property(('name',))
    path = son_property(('path',))
    _type = son_property(('type',))

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
    def get_thumbnail_url(self):
        return ('fotos-cache', (), {'path': self.full_path,
                                   'cache': 'thumb'})

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
    def __init__(self, data):
        super(Foto, self).__init__(data)

class Video(FotoEntity):
    def __init__(self, data):
        super(Video, self).__init__(data)

CACHE_TYPES = (
        'thumb',)

TYPE_MAP = {
        'album':        FotoAlbum,
        'foto':         Foto,
        'video':        Video
    }

# vim: et:sta:bs=2:sw=4:
