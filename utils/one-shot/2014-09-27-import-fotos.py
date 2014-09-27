import _import

from kn import settings
import kn.fotos.entities as fEs

import MySQLdb

def main():
    fEs.ensure_indices()
    creds = settings.PHOTOS_MYSQL_SECRET
    dc = MySQLdb.connect(creds[0], user=creds[1], passwd=creds[2], db=creds[3])
    c = dc.cursor()
    c.execute("SELECT id, name, path, humanname, visibility, description "
                        + "FROM fa_albums")
    print 'albums'
    for oldId, name, path, humanName, visibility, description in c.fetchall():
        if visibility in ('lost', 'deleted'):
            continue
        if fEs.by_oldId('album', oldId) is not None:
            continue
        fEs.entity({
            'type': 'album',
            'oldId': oldId,
            'name': name,
            'path': path,
            'title': humanName,
            'description': description,
            'visibility': [visibility]}).save()
    c.execute("SELECT id, name, path, type, visibility, rotation "
                        + "FROM fa_photos")
    print 'fotos'
    for oldId, name, path, _type, visibility, rotation in c.fetchall():
        if visibility in ('lost', 'deleted'):
            continue
        _type = {'photo': 'foto'}.get(_type, _type)
        if fEs.by_oldId(_type, oldId) is not None:
            continue
        fEs.entity({
            'type': _type,
            'oldId': oldId,
            'name': name,
            'path': path,
            'title': None,
            'description': None,
            'visibility': [visibility],
            'rotation': rotation,
            'cache': []}).save()
    print 'done'

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
