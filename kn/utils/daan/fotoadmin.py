# vim: et:sta:bs=2:sw=4:
import grp
import os
import os.path
import pwd
import random
import re

from django.conf import settings

import kn.fotos.entities as fEs


class FotoadminError(ValueError):
    pass


def fotoadmin_create_event(date, name, humanName):
    if not re.match(r'^20\d{2}-\d{2}-\d{2}$', date):
        raise FotoadminError('Invalid date')
    if not re.match(r'^[a-z0-9-]{3,64}$', name):
        raise FotoadminError('Invalid name')
    event = date + '-' + name
    path = os.path.join(settings.PHOTOS_DIR, event)
    if os.path.isdir(path):
        raise FotoadminError('Event already exists')
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
