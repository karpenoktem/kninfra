import os.path
import logging
import socket
import select
import json
import os

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

        def handle(self, d):
                if d['type'] == 'sync':
                        logging.info("update_db")
                        update_db(self)
                        daan_msgs, cilia_msgs = [], []
                        logging.info("generate: postfix")
                        daan_msgs.append({'type': 'postfix',
                                'map': generate_postfix_map(self)})
                        logging.info("generate: mailman")
                        daan_msgs.append({'type': 'mailman',
                                'changes': generate_mailman_changes(self)})
                        logging.info("generate: wiki")
                        daan_msgs.append({'type': 'wiki',
                                'changes': generate_wiki_changes(self)})
                        logging.info("generate: forum")
                        daan_msgs.append({'type': 'forum',
                                'changes': generate_forum_changes(self)})
                        logging.info("generate: unix")
                        cilia_msgs.append({'type': 'unix',
                                 'map': generate_unix_map(self)})
                        for msg in daan_msgs:
                                logging.info("daan %s" % msg['type'])
                                self.daan.send(msg)
                        for msg in cilia_msgs:
                                logging.info("cilia %s" % msg['type'])
                                self.cilia.send(msg)
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
