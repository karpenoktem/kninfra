# vim: et:sta:bs=2:sw=4:
import threading
import os.path
import logging
import socket
import select
import json
import os

from kn.utils.whim import WhimDaemon

from kn import settings

from kn.utils.cilia.unix import set_unix_map, unix_setpass
from kn.utils.cilia.samba import set_samba_map, samba_setpass
from kn.utils.cilia.fotoadmin import fotoadmin_remove_moved_fotos

class Cilia(WhimDaemon):
    def __init__(self):
        super(Cilia, self).__init__(settings.CILIA_SOCKET)
        self.unix_lock = threading.Lock()
        self.samba_lock = threading.Lock()
        self.fotoadmin_lock = threading.Lock()

    def pre_mainloop(self):
        super(Cilia, self).pre_mainloop()
        if hasattr(settings, 'INFRA_UID'):
            os.chown(settings.CILIA_SOCKET, settings.INFRA_UID, -1)

    def handle(self, d):
        if d['type'] == 'unix':
            with self.unix_lock:
                set_unix_map(self, d['map'])
            # XXX decide where we will call this as this is a bit ugly
            with self.samba_lock:
                set_samba_map(self, d['map'])
        elif d['type'] == 'setpass':
            with self.unix_lock:
                unix_setpass(self, d['user'], d['pass'])
            with self.samba_lock:
                samba_setpass(self, d['user'], d['pass'])
        elif d['type'] == 'fotoadmin-remove-moved-fotos':
            with self.fotoadmin_lock:
                return fotoadmin_remove_moved_fotos(self,
                        d['user'], d['dir'])
