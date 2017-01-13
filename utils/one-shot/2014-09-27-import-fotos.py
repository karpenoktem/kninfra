import _import # noqa: F401

from django.conf import settings
import kn.fotos.entities as fEs
import kn.leden.entities as Es

import MySQLdb
import random

def main():
    fEs.ensure_indices()
    creds = settings.PHOTOS_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2], db=creds[3])
    c = dc.cursor()

    if fEs.by_path('') is None:
        root = fEs.entity({
            'type': 'album',
            'path': None,
            'name': '',
            'title': 'Karpe Noktem fotoalbum',
            'description': "De fotocollectie van Karpe Noktem",
            'random': random.random(),
            'visibility': ['world']})
        root.update_metadata(None, save=False)
        root.save()

    print 'albums'
    c.execute("SELECT id, name, path, humanname, visibility, description "
                        + "FROM fa_albums ORDER BY path")
    for oldId, name, path, humanName, visibility, description in c.fetchall():
        if path and not path.endswith('/'):
            continue
        if fEs.by_oldId('album', oldId) is not None:
            continue

        data = {'type': 'album',
                'oldId': oldId,
                'path': path.strip('/'),
                'name': name,
                'title': humanName,
                'description': description,
                'random': random.random()}

        if visibility == 'lost':
            visibility = []
            data['lost'] = True
        elif visibility == 'deleted':
            visibility = []
        else:
            visibility = [visibility]
        data['visibility'] = visibility

        album = fEs.entity(data)
        album.update_metadata(album.get_parent(), save=False)
        album.save()

    print 'fotos'
    c.execute("SELECT id, name, path, visibility, rotation FROM fa_photos")
    for oldId, name, path, visibility, rotation in c.fetchall():
        if fEs.by_oldId('foto', oldId) is not None:
            continue

        data = {'type': 'foto',
                'oldId': oldId,
                'path': path.strip('/'),
                'name': name,
                'random': random.random(),
                'rotation': rotation}

        if visibility == 'lost':
            visibility = []
            data['lost'] = True
        elif visibility == 'deleted':
            visibility = []
        else:
            visibility = [visibility]
        data['visibility'] = visibility

        foto = fEs.entity(data)
        foto.update_metadata(foto.get_parent(), save=False)
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
