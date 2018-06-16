# vim: et:sta:bs=2:sw=4:
import os
import os.path
import threading

from django.conf import settings

from kn.utils.daan._ldap import apply_ldap_changes, ldap_setpass
from kn.utils.daan.fotoadmin import (fotoadmin_create_event,
                                     fotoadmin_move_fotos)
from kn.utils.daan.postfix import set_postfix_map, set_postfix_slm_map
from kn.utils.daan.wiki import apply_wiki_changes
from kn.utils.whim import WhimDaemon


class Daan(WhimDaemon):

    def __init__(self):
        super(Daan, self).__init__(settings.DAAN_SOCKET)
        self.postfix_lock = threading.Lock()
        self.postfix_slm_lock = threading.Lock()
        self.wiki_lock = threading.Lock()
        self.ldap_lock = threading.Lock()
        self.fotoadmin_lock = threading.Lock()

    def pre_mainloop(self):
        super(Daan, self).pre_mainloop()
        os.chown(settings.DAAN_SOCKET, settings.INFRA_UID, -1)
        self.notify_systemd()

    def handle(self, d):
        if d['type'] == 'postfix':
            with self.postfix_lock:
                return set_postfix_map(self, d['map'])
        elif d['type'] == 'postfix-slm':
            with self.postfix_slm_lock:
                return set_postfix_slm_map(self, d['map'])
        elif d['type'] == 'wiki':
            with self.wiki_lock:
                return apply_wiki_changes(self, d['changes'])
        elif d['type'] == 'ldap':
            with self.ldap_lock:
                return apply_ldap_changes(self, d['changes'])
        elif d['type'] == 'setpass':
            with self.ldap_lock:
                ldap_setpass(self, d['user'], d['pass'])
        elif d['type'] == 'fotoadmin-create-event':
            with self.fotoadmin_lock:
                return fotoadmin_create_event(self, d['date'],
                                              d['name'], d['humanname'])
        elif d['type'] == 'fotoadmin-move-fotos':
            with self.fotoadmin_lock:
                return fotoadmin_move_fotos(self, d['event'],
                                            d['store'], d['user'], d['dir'])
