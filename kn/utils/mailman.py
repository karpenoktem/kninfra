# vim: et:sta:bs=2:sw=4:
import os.path

from kn.base.runtime import setup_virtual_package
from django.conf import settings

__mailman_imported = False

def import_mailman():
    global __mailman_imported
    if __mailman_imported:
        return
    try:
        import Mailman
    except ImportError:
        setup_virtual_package('Mailman', os.path.join(
            settings.MAILMAN_PATH, 'Mailman'))
    __mailman_imported = True
