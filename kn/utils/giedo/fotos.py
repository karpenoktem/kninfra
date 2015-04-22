from kn import settings
import kn.fotos.entities as fEs
import kn.leden.entities as Es

import os
import random

extensions = {
    'gif': 'gif',
    'jpg': 'jpeg',
    'jpeg': 'jpeg',
    'png': 'png',
    'bmp': 'bmp',
}

def list_album(album):
    fotos = {}
    for foto in album.list_all():
        fotos[foto.name] = foto
    return fotos

def scan_album(album):
    fotos = list_album(album)

    names = os.listdir(os.path.join(settings.PHOTOS_DIR, album.full_path))
    names.sort()
    for name in names:
        filepath = os.path.join(settings.PHOTOS_DIR, album.full_path, name)
        if name[0] == '.':
            continue
        entity = fotos.get(name, None)
        if entity is not None and entity.is_lost:
            entity.found(album)
        if os.path.isdir(filepath):
            # album
            if entity is None:
                entity = fEs.entity({
                    'type': 'album',
                    'path': album.full_path,
                    'name': name,
                    'random': random.random(),
                    'visibility': ['hidden']})
                entity.update_metadata(album, save=False)
                entity.save()
            elif entity.update_metadata(album, save=False):
                entity.save()
            scan_album(entity)

        elif os.path.splitext(name)[1][1:].lower() in extensions:
            # photo
            entity = fotos.get(name, None)
            if entity is None:
                entity = fEs.entity({
                    'type': 'foto',
                    'path': album.full_path,
                    'name': name,
                    'random': random.random(),
                    'visibility': ['world']})
                entity.update_metadata(album, save=False)
                entity.save()
            elif entity.update_metadata(album, save=False):
                entity.save()

    for entity in fotos.values():
        if entity.name not in names:
            entity.lost(album)


def scan_fotos():
    album = fEs.by_path('')
    if album is None:
        album = fEs.entity({
            'type': 'album',
            'name': '',
            'path': None,
            'random': random.random(),
            'title': 'Karpe Noktem fotoalbum',
            'description': "De fotocollectie van Karpe Noktem",
            'visibility': ['world']})
        album.update_metadata(None)
        album.save()
    elif album.update_metadata(None):
        album.save()
    scan_album(album)

    return {'success': True}

