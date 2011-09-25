import threading
import os.path
import logging
import socket
import select
import json
import os
import subprocess

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
                self.update_knsite_lock = threading.Lock()
                self.update_knforum_lock = threading.Lock()
                self.fotoadmin_lock = threading.Lock()

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
                elif d['type'] == 'update-knsite':
                        with self.update_knsite_lock:
                                return self.start_external(['update-knsite.sh'],
                                        cwd=path.dirname(__file__))
                elif d['type'] == 'update-knfotos':
                        with self.update_knfotos_lock:
                                return self.start_external(
                                        ['update-knfotos.sh'],
                                        cwd=path.dirname(__file__))
                elif d['type'] == 'fotoadmin-create-event':
                        with self.fotoadmin_lock:
                                return self.start_external(
                                        ['fotoadmin-create-event.php',
                                        d['date'], d['name'], d['humanname']],
                                        cwd=path.dirname(__file__))
                elif d['type'] == 'fotoadmin-move-fotos':
                        with self.fotoadmin_lock:
                                return self.start_external(
                                        ['fotoadmin-move-fotos.php', d['event'],
                                        d['user'], d['dir']],
                                        cwd=path.dirname(__file__))

        def start_external(args, cwd=None):
                ph = subprocess.Popen(args, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
                ph.stdin.close()
                (output, ) = ph.communicate()
                return output

