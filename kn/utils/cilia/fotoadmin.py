import subprocess
import os.path
import re

from kn import settings
from kn.fotos.forms import foto_dirs

def fotoadmin_remove_moved_fotos(cilia, store, user, directory):
    if not re.match('^[a-z0-9]{3,32}$', user):
        return {'error': 'Invalid user'}
    if not re.match('^[^/\\.][^/]*$', directory):
        return {'error': 'Invalid dir'}
    if not store in foto_dirs:
        return {'error': 'Invalid store'}
    root, between = foto_dirs[store]
    user_path = os.path.join(root, user)
    if not os.path.isdir(user_path):
        return {'error': 'Invalid user'}
    fotos_path = os.path.join(user_path, between, directory)
    if not os.path.isdir(fotos_path):
        return {'error': 'Invalid fotodir'}
    if not os.path.realpath(fotos_path).startswith(user_path):
        return {'error': 'Security exception'}
    subprocess.call(['rm', '-rf', fotos_path])
    return {'success': True}

# vim: et:sta:bs=2:sw=4:
