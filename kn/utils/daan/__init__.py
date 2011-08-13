import os.path
import logging
import socket
import select
import json
import os

from kn.utils.whim import WhimDaemon

from kn import settings

class Daan(WhimDaemon):
        def __init__(self):
                super(Daan, self).__init__(settings.DAAN_SOCKET)

        def handle(self, d):
                pass
