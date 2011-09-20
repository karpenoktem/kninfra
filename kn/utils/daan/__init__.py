import threading
import os.path
import logging
import socket
import select
import json
import os

from kn.utils.whim import WhimDaemon
from kn.utils.daan.postfix import set_postfix_map
from kn.utils.daan.mailman import apply_mailman_changes
from kn.utils.daan.wiki import apply_wiki_changes, wiki_setpass
from kn.utils.daan.forum import apply_forum_changes, forum_setpass

from kn import settings

class Daan(WhimDaemon):
        def __init__(self):
                super(Daan, self).__init__(settings.DAAN_SOCKET)
                self.postfix_lock = threading.Lock()
                self.mailman_lock = threading.Lock()
                self.wiki_lock = threading.Lock()
                self.forum_lock = threading.Lock()

        def pre_mainloop(self):
                super(Daan, self).pre_mainloop()
                os.chown(settings.DAAN_SOCKET, settings.INFRA_UID, -1)

        def handle(self, d):
                if d['type'] == 'postfix':
                        with self.postfix_lock:
                                return set_postfix_map(self, d['map'])
                elif d['type'] == 'mailman':
                        with self.mailman_lock:
                                return apply_mailman_changes(self,
                                                d['changes'])
                elif d['type'] == 'wiki':
                        with self.wiki_lock:
                                return apply_wiki_changes(self, d['changes'])
                elif d['type'] == 'forum':
                        with self.forum_lock:
                                return apply_forum_changes(self, d['changes'])
                elif d['type'] == 'setpass':
                        with self.wiki_lock:
                                wiki_setpass(self, d['user'], d['pass'])
                        with self.forum_lock:
                                forum_setpass(self, d['user'], d['pass'])

