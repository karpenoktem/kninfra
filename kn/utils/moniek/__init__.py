import logging
import yaml
import os.path

from koert.gnucash import tools as koerttools

from django.conf import settings

from kn.utils.moniek import fin
from kn.utils.whim import WhimDaemon


class Moniek(WhimDaemon):

    def __init__(self):
        super(Moniek, self).__init__(settings.MONIEK_SOCKET)

        with open(settings.FIN_YAML_PATH) as f:
            self.settings = yaml.load(f)

    def handle(self, d):
        if d['type'] == 'fin-get-account':
            return fin.get_account(
                self, d['name'], d['full_name'], d['account_type'])
        elif d['type'] == 'fin-get-debitors':
            return fin.get_debitors(self)
        elif d['type'] == 'fin-check-names':
            return fin.check_names(self, d['names'])
        elif d['type'] == 'fin-get-gnucash-object':
            return fin.get_gnucash_object(self, d['year'], d['handle'])
        else:
            logging.info('unknown command type: %s', repr(d['type']))

    @property
    def gcf(self):
        return self.gcf_by_year(self.settings['current year'])

    def gcf_by_year(self, year):
        if year not in self.settings['years']:
            return None
        # TODO: add more caching?
        relpath = self.settings['years'][year]
        path = os.path.join(os.path.dirname(settings.FIN_YAML_PATH),relpath)
        return koerttools.open_yaml(path)

# vim: et:sta:bs=2:sw=4:
