import os.path
import logging
import socket
import select
import json
import os

from kn.utils.whim import WhimDaemon

from kn import settings

class Cilia(WhimDaemon):
        def __init__(self):
                super(Cilia, self).__init__(settings.CILIA_BIND_ADDR,
                                family='tcp')

        def handle(self, d):
                pass
