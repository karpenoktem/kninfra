import os.path
import logging
import socket
import select
import json
import os

from kn.utils.whim import WhimDaemon

from kn import settings

from kn.utils.giedo.db import update_db
from kn.utils.giedo.postfix import update_postfix

class Giedo(WhimDaemon):
        def __init__(self):
                super(Giedo, self).__init__(settings.GIEDO_SOCKET)

        def handle(self, d):
                # For now, be stupid, and always update everything
                update_db(self)
                update_postfix(self)
