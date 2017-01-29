# vim: et:sta:bs=2:sw=4:
import grp
import os
import os.path
import pwd
import random
import re
import subprocess

from django.conf import settings

import kn.fotos.entities as fEs
from kn.fotos.roots import FOTO_ROOTS


def fotoadmin_create_event(daan, date, name, humanName):
    if not re.match('^20\d{2}-\d{2}-\d{2}$', date):
        return {'error': 'Invalid date'}
    if not re.match('^[a-z0-9-]{3,64}$', name):
        return {'error': 'Invalid name'}
    event = date + '-' + name
    path = os.path.join(settings.PHOTOS_DIR, event)
    if os.path.isdir(path):
        return {'error': 'Event already exists'}
    os.mkdir(path, 0o775)
    os.chown(path, pwd.getpwnam('fotos').pw_uid,
             grp.getgrnam('fotos').gr_gid)
    album = fEs.entity({
        'type': 'album',
        'path': '',
        'name': event,
        'random': random.random(),
        'visibility': ['hidden'],
        'title': humanName})
    album.update_metadata(album.get_parent(), save=False)
    album.save()
    return {'success': True}


def fotoadmin_move_fotos(daan, event, store, user, directory):
    if not re.match('^20\d{2}-\d{2}-\d{2}-[a-z0-9-]{3,64}$', event):
        return {'error': 'Invalid event'}
    if not re.match('^[a-z0-9]{3,32}$', user):
        return {'error': 'Invalid user'}
    if not re.match('^[^/\\.][^/]*$', directory):
        return {'error': 'Invalid dir'}
    if store not in FOTO_ROOTS:
        return {'error': 'Invalid store'}
    root = FOTO_ROOTS[store]
    user_path = os.path.join(root.base, user)
    if not os.path.isdir(user_path):
        return {'error': 'Invalid user'}
    fotos_path = os.path.join(user_path, root.between, directory)
    if not os.path.isdir(fotos_path):
        return {'error': 'Invalid fotodir'}
    if not os.path.realpath(fotos_path).startswith(user_path):
        return {'error': 'Security exception'}
    target_path = os.path.join(settings.PHOTOS_DIR, event)
    if not os.path.isdir(target_path):
        return {'error': 'Event does not exist'}
    base_target_path = os.path.join(target_path, user)
    target_path = base_target_path
    i = 1
    while os.path.isdir(target_path):
        i += 1
        target_path = base_target_path + str(i)
    if subprocess.call(['cp', '-r', fotos_path, target_path]) != 0:
        return {'error': 'cp -r failed'}
    if subprocess.call(['chown', '-R', 'fotos:fotos', target_path]) != 0:
        return {'error': 'chown failed'}
    if subprocess.call(['chmod', '-R', '644', target_path]) != 0:
        return {'error': 'chmod failed'}
    if subprocess.call(['find', target_path, '-type', 'd', '-exec',
                        'chmod', '755', '{}', '+']) != 0:
        return {'error': 'chmod (dirs) failed'}
    return {'success': True}
