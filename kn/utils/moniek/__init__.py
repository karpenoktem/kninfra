import logging

from django.conf import settings

from koert.gnucash.tools import open_gcf_in_git_repo

from kn.utils.whim import WhimDaemon

from kn.utils.moniek.fin import fin_get_account, fin_get_debitors


class Moniek(WhimDaemon):

    def __init__(self):
        super(Moniek, self).__init__(settings.MONIEK_SOCKET)

    def handle(self, d):
        if d['type'] == 'fin-get-account':
            return fin_get_account(self, d['name'], d['full_name'])
        elif d['type'] == 'fin-get-debitors':
            return fin_get_debitors(self)
        else:
            logging.info('unknown command type: %s', repr(d['type']))

    @property
    def gcf(self):
        # TODO: add caching
        return open_gcf_in_git_repo(
            settings.FIN_REPO_PATH,
            settings.FIN_FILENAME,
            cachepath=settings.FIN_CACHE_PATH)

# vim: et:sta:bs=2:sw=4:
