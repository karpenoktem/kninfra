import threading
import os.path
import logging
import socket
import select
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

        def sync_postfix(self):
                logging.info("postfix: generate")
                msg = {'type': 'postfix',
                        'map': generate_postfix_map(self)}
                logging.info("postfix: daan")
                self.daan.send(msg)
                logging.info("postfix: done")
        def sync_mailman(self):
                logging.info("mailman: generate")
                msg = {'type': 'mailman',
                        'changes': generate_mailman_changes(
                                                self)}
                logging.info("mailman: daan")
                self.daan.send(msg)
                logging.info("mailman: done")
        def sync_wiki(self):
                logging.info("wiki: generate")
                msg = {'type': 'wiki',
                        'changes': generate_wiki_changes(self)}
                logging.info("wiki: daan")
                self.daan.send(msg)
                logging.info("wiki: done")
        def sync_forum(self):
                logging.info("forum: generate")
                msg = {'type': 'forum',
                        'changes': generate_forum_changes(self)}
                logging.info("forum: daan")
                self.daan.send(msg)
                logging.info("forum: done")
        def sync_unix(self):
                logging.info("unix: generate")
                msg = {'type': 'unix',
                         'map': generate_unix_map(self)}
                logging.info("unix: cilia")
                self.cilia.send(msg)
                logging.info("unix: done")

        def sync(self):
                logging.info("update_db")
                update_db(self)
                actions = (self.sync_mailman, self.sync_unix,
                                self.sync_postfix, self.sync_forum)
                todo = [len(actions)]
                todo_lock = threading.Lock()
                todo_event = threading.Event()
                def _entry(act):
                        act()
                        with todo_lock:
                                todo[0] -= 1
                                if todo[0] == 0:
                                        todo_event.set()
                for act in actions:
                        self.threadPool.execute(_entry, act)
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
