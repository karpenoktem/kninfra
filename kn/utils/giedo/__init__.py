import threading
import os.path
import logging
import socket
import select
import time
import json
import os

import mirte # github.com/bwesterb/mirte

import kn.leden.entities as Es

from kn.utils.whim import WhimDaemon, WhimClient

from kn import settings

from kn.utils.giedo.db import update_db
from kn.utils.giedo.postfix import generate_postfix_map
from kn.utils.giedo.mailman import generate_mailman_changes
from kn.utils.giedo.wiki import generate_wiki_changes
from kn.utils.giedo.forum import generate_forum_changes
from kn.utils.giedo.unix import generate_unix_map

class Giedo(WhimDaemon):
        def __init__(self):
                super(Giedo, self).__init__(settings.GIEDO_SOCKET)
                self.daan = WhimClient(settings.DAAN_SOCKET)
                self.cilia = WhimClient(settings.CILIA_SOCKET)
                self.mirte = mirte.get_a_manager()
                self.threadPool = self.mirte.get_a('threadPool')
                self.operation_lock = threading.Lock()
                self.ss_actions = (
                              ('postfix', self.daan, self._gen_postfix),
                              ('mailman', self.daan, self._gen_mailman),
                              ('forum', self.daan, self._gen_forum),
                              ('unix', self.cilia, self._gen_unix),
                              ('wiki', self.daan, self._gen_wiki))


        def _gen_postfix(self):
                return {'type': 'postfix',
                        'map': generate_postfix_map(self)}
        def _gen_mailman(self):
                return {'type': 'mailman',
                        'changes': generate_mailman_changes(
                                                self)}
        def _gen_wiki(self):
                return {'type': 'wiki',
                        'changes': generate_wiki_changes(self)}
        def _gen_forum(self):
                return {'type': 'forum',
                        'changes': generate_forum_changes(self)}
        def _gen_unix(self):
                return  {'type': 'unix',
                         'map': generate_unix_map(self)}

        def sync(self):
                update_db_start = time.time()
                update_db(self)
                logging.info("update_db %s" % (time.time() - update_db_start))
                todo = [len(self.ss_actions)]
                todo_lock = threading.Lock()
                todo_event = threading.Event()
                def _entry(name, daemon, action):
                        start = time.time()
                        msg = action()
                        elapsed = time.time() - start
                        logging.info("generate %s %s" % (name, elapsed))
                        start = time.time()
                        daemon.send(msg)
                        elapsed = time.time() - start
                        logging.info("send %s %s" % (name, elapsed))
                        with todo_lock:
                                todo[0] -= 1
                                if todo[0] == 0:
                                        todo_event.set()
                for act in self.ss_actions:
                        self.threadPool.execute(_entry, *act)
                todo_event.wait()

        def handle(self, d):
                with self.operation_lock:
                        if d['type'] == 'sync':
                                return self.sync()
                        elif d['type'] == 'setpass':
                                u = Es.by_name(d['user'])
                                if u is None:
                                        return {'error': 'no such user'}
                                u = u.as_user()
                                if not u.check_password(d['oldpass']):
                                        return {'error': 'wrong old password'}
                                u.set_password(d['newpass'])
                                d2 = {'type': 'setpass',
                                      'user': d['user'],
                                      'pass': d['newpass']}
                                self.daan.send(d2)
                                self.cilia.send(d2)
                                return {'success': True}
                        elif d['type'] == 'fotoadmin-move-fotos':
                                ret = self.daan.send(d)
                                if 'success' not in ret:
                                        return ret
                                return self.cilia.send({
                                        'type': 'fotoadmin-remove-moved-fotos',
                                        'user': d['user'],
                                        'dir': d['dir'],
                                        })
                        elif d['type'] in ['update-knsite', 'update-knfotos',
                                        'fotoadmin-create-event']:
                                return self.daan.send(d)
                        else:
                                print "Unknown command: %s" % d['type']
