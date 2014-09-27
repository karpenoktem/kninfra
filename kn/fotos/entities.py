from kn.leden.mongo import db, SONWrapper, _id, son_property

fcol = db['fotos']

def ensure_indices():
    fcol.ensure_index([('type',1), ('oldId', 1)], sparse=True)
    fcol.ensure_index([('path', 1), ('name', 1)])
    fcol.ensure_index('tags', sparse=True)
    fcol.ensure_index('cache', sparse=True)
    fcol.ensure_index([('path', 1), ('visibility', 1)])

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
    return by_path_and_name(pp, n)

class FotoEntity(SONWrapper):
    def __init__(self, data):
        super(FotoEntity, self).__init__(data, fcol)

    @property
    def id(self):
        return str(self._data['_id'])

    oldId = son_property(('oldId',))
    name = son_property(('name',))
    title = son_property(('title',))
    description = son_property(('description',))
    visibility = son_property(('visibility',))

class FotoAlbum(FotoEntity):
    def __init__(self, data):
        super(FotoAlbum, self).__init__(data)

class Foto(FotoEntity):
    def __init__(self, data):
        super(Foto, self).__init__(data)

class Video(FotoEntity):
    def __init__(self, data):
        super(Video, self).__init__(data)

TYPE_MAP = {
        'album':        FotoAlbum,
        'foto':         Foto,
        'video':        Video
    }

# vim: et:sta:bs=2:sw=4:
