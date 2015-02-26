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
    fotos = {}
    for foto in album.list_all():
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
                subalbum.update_metadata(album, save=False)
                subalbum.save()
            elif subalbum.update_metadata(album, save=False):
                subalbum.save()
            scan(subalbum)

        elif os.path.splitext(name)[1][1:].lower() in extensions:
            # photo
            foto = fotos.get(name, None)
            if foto is None:
                foto = fEs.entity({
                    'type': 'foto',
                    'path': album.full_path,
                    'name': name,
                    'random': random.random(),
                    'visibility': ['world']})
                foto.update_metadata(album, save=False)
                foto.save()
            elif foto.update_metadata(album, save=False):
                foto.save()

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
        album.update_metadata(None)
        album.save()
    elif album.update_metadata(None):
        album.save()
    scan(album)



if __name__ == '__main__':
    main()
