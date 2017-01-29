import subprocess
import os.path
import re

import six

from kn.fotos.roots import FOTO_ROOTS


def fotoadmin_remove_moved_fotos(cilia, store, user, directory):
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
    subprocess.call(['rm', '-rf', fotos_path])
    return {'success': True}


def fotoadmin_scan_userdirs():
    userdirs = []
    for store, root in six.iteritems(FOTO_ROOTS):
        for user in os.listdir(root.base):
            if user[0] == '.':
                continue
            fotodir = os.path.join(root.base, user, root.between)
            if not os.path.isdir(fotodir):
                continue
            for name in os.listdir(fotodir):
                if fotodir[0] == '.' or not os.path.isdir(
                        os.path.join(fotodir, name)):
                    continue
                path = user + '/' + name
                userdirs.append((store + '/' + path, path))
    return userdirs

# vim: et:sta:bs=2:sw=4:
