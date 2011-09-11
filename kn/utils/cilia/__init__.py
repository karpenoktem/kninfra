import os.path
import logging
import socket
import select
import json
import os

from kn.utils.whim import WhimDaemon

from kn import settings

from kn.utils.cilia.unix import set_unix_map, unix_setpass

class Cilia(WhimDaemon):
        def __init__(self):
                super(Cilia, self).__init__(settings.CILIA_SOCKET)

        def handle(self, d):
                if d['type'] == 'unix':
                        return set_unix_map(self, d['map'])
                elif d['type'] == 'setpass':
                        return unix_setpass(self, d['user'], d['pass'])
