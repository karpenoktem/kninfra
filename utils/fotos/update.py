import _import

from kn import settings
import kn.fotos.entities as fEs
import kn.leden.entities as Es

import os
import random
import Image
from PIL.ExifTags import TAGS

extensions = {
    'gif': 'gif',
    'jpg': 'jpeg',
    'jpeg': 'jpeg',
    'png': 'png',
    'bmp': 'bmp',
}

def getexif(path):
    img = Image.open(path)
    if not hasattr(img, '_getexif'):
        return {}
    exif = img._getexif()
    for k, v in exif.items():
        if k not in TAGS:
            continue
        exif[TAGS[k]] = v
    return exif

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
                exif = getexif(filepath)
                orientation = 0
                exif_orientation = int(exif.get('Orientation', '1'))
                if exif_orientation == 1:
                    orientation = 0
                elif exif_orientation == 3:
                    orientation = 180
                elif exif_orientation == 6:
                    orientation = 90
                elif exif_orientation == 8:
                    orientation = 270
                # other orientations are mirrored, and won't occur much in practice

                fEs.entity({
                    'type': 'foto',
                    'path': album.full_path,
                    'name': name,
                    'random': random.random(),
                    'orientation': orientation,
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
