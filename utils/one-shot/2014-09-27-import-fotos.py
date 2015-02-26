import _import

from kn import settings
import kn.fotos.entities as fEs
import kn.leden.entities as Es

import MySQLdb
import random

def main():
    fEs.ensure_indices()
    creds = settings.PHOTOS_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2], db=creds[3])
    c = dc.cursor()
    c.execute("SELECT id, name, path, humanname, visibility, description "
                        + "FROM fa_albums")
    print 'albums'
    if fEs.by_path('') is None:
        root = fEs.entity({
            'type': 'album',
            'name': '',
            'path': None,
            'random': random.random(),
            'title': 'Karpe Noktem fotoalbum',
            'description': "De fotocollectie van Karpe Noktem",
            'visibility': ['world']})
        root.update_metadata(None)
        root.save()
    for oldId, name, path, humanName, visibility, description in c.fetchall():
        if visibility in ('lost', 'deleted'):
            continue
        if fEs.by_oldId('album', oldId) is not None:
            continue
        path = path.strip('/')
        album = fEs.entity({
            'type': 'album',
            'oldId': oldId,
            'random': random.random(),
            'name': name,
            'path': path,
            'title': humanName,
            'description': description,
            'visibility': [visibility]})
        album.update_metadata(album.get_parent())
        album.save()
    c.execute("SELECT id, name, path, visibility, rotation FROM fa_photos")
    print 'fotos'
    for oldId, name, path, visibility, rotation in c.fetchall():
        if visibility in ('lost', 'deleted'):
            continue
        if fEs.by_oldId('foto', oldId) is not None:
            continue
        path = path.strip('/')
        foto = fEs.entity({
            'type': 'foto',
            'oldId': oldId,
            'name': name,
            'random': random.random(),
            'path': path,
            'title': None,
            'description': None,
            'visibility': [visibility],
            'rotation': rotation})
        foto.update_metadata(foto.get_parent())
        foto.save()
    print 'tags'
    c.execute("SELECT photo_id, username FROM fa_tags")
    for oldId, username in c.fetchall():
        foto = fEs.by_oldId('foto', oldId)
        if foto is None:
            continue
        user = Es.by_name(username)
        if user is None:
            continue
        if not 'tags' in foto._data:
            foto._data['tags'] = []
        if not user._id in foto._data['tags']:
            foto._data['tags'].append(user._id)
            foto.save()
    print 'done'

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
