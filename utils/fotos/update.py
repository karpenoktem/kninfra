import _import

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
    _fotos = album.list('system')
    fotos = {}
    for foto in _fotos:
        fotos[foto.name] = foto
    return fotos

def scan(album):
    fotos = list_album(album)

    names = os.listdir(os.path.join(settings.PHOTOS_DIR, album.full_path))
    names.sort()
    for name in names:
        filepath = os.path.join(settings.PHOTOS_DIR, album.full_path, name)
        if name[0] == '.':
            continue
        if os.path.isdir(filepath):
            # album
            subalbum = fotos.get(name, None)
            if subalbum is None:
                subalbum = fEs.entity({
                    'type': 'album',
                    'path': album.full_path,
                    'name': name,
                    'random': random.random(),
                    'visibility': ['hidden']})
                subalbum.save()
            scan(subalbum)
        elif os.path.splitext(name)[1][1:].lower() in extensions:
            # photo
            if name not in fotos:
                fEs.entity({
                    'type': 'foto',
                    'path': album.full_path,
                    'name': name,
                    'random': random.random(),
                    'visibility': ['hidden']}).save()

    # TODO deleted albums



def main():
    fEs.ensure_indices()
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
        album.save()
    scan(album)



if __name__ == '__main__':
    main()
