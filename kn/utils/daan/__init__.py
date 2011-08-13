import os.path
import logging
import socket
import select
import json
import os

from kn.utils.whim import WhimDaemon
from kn.utils.daan.postfix import set_postfix_map

from kn import settings

class Daan(WhimDaemon):
        def __init__(self):
                super(Daan, self).__init__(settings.DAAN_SOCKET)

        def pre_mainloop(self):
                super(Daan, self).pre_mainloop()
                os.chown(settings.DAAN_SOCKET, settings.INFRA_UID, -1)

        def handle(self, d):
                if d['type'] == 'postfix':
                        return set_postfix_map(self, d['map'])
