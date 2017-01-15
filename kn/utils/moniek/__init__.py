import os.path
import logging

from django.conf import settings

from kn.utils.whim import WhimDaemon

from kn.utils.moniek.fin import fin_get_account


class Moniek(WhimDaemon):

    def __init__(self):
        super(Moniek, self).__init__(settings.MONIEK_SOCKET)

    def handle(self, d):
        if d['type'] == 'fin-get-account':
            return fin_get_account(self, d['name'], d['full_name'])
        else:
            logging.info('unknown command type: %s', repr(d['type']))

# vim: et:sta:bs=2:sw=4:
