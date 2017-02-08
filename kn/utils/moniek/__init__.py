import logging

from koert.gnucash.tools import open_yaml

from django.conf import settings

import fin
from kn.utils.whim import WhimDaemon


class Moniek(WhimDaemon):

    def __init__(self):
        super(Moniek, self).__init__(settings.MONIEK_SOCKET)

    def handle(self, d):
        if d['type'] == 'fin-get-account':
            return fin.get_account(
                self, d['name'], d['full_name'], d['account_type'])
        elif d['type'] == 'fin-get-debitors':
            return fin.get_debitors(self)
        elif d['type'] == 'fin-check-names':
            return fin.check_names(self, d['names'])
        else:
            logging.info('unknown command type: %s', repr(d['type']))

    @property
    def gcf(self):
        # TODO: add caching
        return open_yaml(settings.FIN_YAML_PATH)

# vim: et:sta:bs=2:sw=4:
