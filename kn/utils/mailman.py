from __future__ import absolute_import

import os.path

from django.conf import settings
from django.utils import six

from kn.base.runtime import setup_virtual_package

__mailman_imported = False


def import_mailman():
    global __mailman_imported
    if six.PY3:
        return  # HACK see #438
    if __mailman_imported:
        return
    try:
        import Mailman  # noqa: F401
    except ImportError:
        setup_virtual_package('Mailman', os.path.join(
            settings.MAILMAN_PATH, 'Mailman'))
    __mailman_imported = True

# vim: et:sta:bs=2:sw=4:
