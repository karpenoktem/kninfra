import os.path

from django.conf import settings

from kn.base.runtime import setup_virtual_package

setup_virtual_package(
    'Mailman',
    os.path.join(settings.MAILMAN_PATH, 'Mailman')
)

from Mailman import Utils, MailList, UserDesc, Errors  # noqa: E402 isort:skip

__all__ = ['Utils', 'MailList', 'UserDesc', 'Errors']
