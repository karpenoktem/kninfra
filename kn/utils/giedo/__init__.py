import os.path
import logging
import socket
import select
import json
import os

from kn.utils.unixjsondaemon import UnixJSONDaemon

from kn import settings

from kn.utils.giedo.db import update_db
from kn.utils.giedo.postfix import update_postfix

class Giedo(UnixJSONDaemon):
        def __init__(self):
                super(Giedo, self).__init__(settings.GIEDO_SOCKET)

        def handle(self, d):
                # For now, be stupid, and always update the database
                update_db()
                update_postfix()
