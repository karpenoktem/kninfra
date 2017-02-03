import time
import logging
import threading

import mirte  # github.com/bwesterb/mirte

from django.conf import settings
from kn.utils.whim import WhimDaemon, WhimClient
import kn.leden.entities as Es

from kn.utils.giedo.db import update_db
from kn.utils.giedo.postfix import (generate_postfix_map,
                                    generate_postfix_slm_map)
from kn.utils.giedo.mailman import generate_mailman_changes
from kn.utils.giedo.wiki import generate_wiki_changes
from kn.utils.giedo.forum import generate_forum_changes
from kn.utils.giedo.unix import generate_unix_map
from kn.utils.giedo.openvpn import (create_openvpn_installer,
                                    create_openvpn_zip, generate_openvpn_zips)
from kn.utils.giedo.siteagenda import update_site_agenda
from kn.utils.giedo._ldap import generate_ldap_changes
from kn.utils.giedo.wolk import generate_wolk_changes
from kn.utils.giedo.quassel import generate_quassel_changes
from kn.utils.giedo.fotos import scan_fotos


class Giedo(WhimDaemon):

    def __init__(self):
        super(Giedo, self).__init__(settings.GIEDO_SOCKET)
        self.l = logging.getLogger('giedo')
        self.last_sync_ts = 0
        self.daan, self.cilia, self.moniek = None, None, None
        try:
            self.daan = WhimClient(settings.DAAN_SOCKET)
        except:
            self.l.exception("Couldn't connect to daan")
        try:
            self.cilia = WhimClient(settings.CILIA_SOCKET)
        except:
            self.l.exception("Couldn't connect to cilia")
        try:
            self.moniek = WhimClient(settings.MONIEK_SOCKET)
        except:
            self.l.exception("Couldn't connect to moniek")
        self.mirte = mirte.get_a_manager()
        self.threadPool = self.mirte.get_a('threadPool')
        self.operation_lock = threading.Lock()
        self.openvpn_lock = threading.Lock()
        self.ss_actions = (
            ('postfix', self.daan, self._gen_postfix),
            ('postfix-slm', self.daan, self._gen_postfix_slm),
            ('mailman', self.daan, self._gen_mailman),
            ('forum', self.daan, self._gen_forum),
            ('unix', self.cilia, self._gen_unix),
            ('wiki', self.daan, self._gen_wiki),
            ('ldap', self.daan, self._gen_ldap),
            ('wolk', self.cilia, self._gen_wolk),
            ('quassel', self.daan, self._gen_quassel))

    def _gen_quassel(self):
        return {'type': 'quassel',
                'changes': generate_quassel_changes(self)}

    def _gen_wolk(self):
        return {'type': 'wolk',
                'changes': generate_wolk_changes(self)}

    def _gen_ldap(self):
        return {'type': 'ldap',
                'changes': generate_ldap_changes(self)}

    def _gen_postfix_slm(self):
        return {'type': 'postfix-slm',
                'map': generate_postfix_slm_map(self)}

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
        return {'type': 'unix',
                'map': generate_unix_map(self)}

    def _sync_openvpn(self):
        with self.openvpn_lock:
            generate_openvpn_zips(self)

    def sync(self):
        update_db_start = time.time()
        update_db(self)
        logging.info("update_db %s" % (time.time() - update_db_start))
        todo = [len(self.ss_actions)]
        todo_lock = threading.Lock()
        todo_event = threading.Event()

        def _sync_action(func, *args):
            try:
                func(*args)
            except Exception:
                logging.exception("Uncaught exception")
            with todo_lock:
                todo[0] -= 1
                if todo[0] == 0:
                    todo_event.set()

        def _entry(name, daemon, action):
            start = time.time()
            msg = action()
            elapsed = time.time() - start
            logging.info("generate %s %s" % (name, elapsed))
            start = time.time()
            daemon.send(msg)
            elapsed = time.time() - start
            logging.info("send %s %s" % (name, elapsed))

        for act in self.ss_actions:
            self.threadPool.execute(_sync_action, _entry, *act)
        self.threadPool.execute(self._sync_openvpn)
        todo_event.wait()
        self.last_sync_ts = time.time()

    def handle(self, d):
        if d['type'] == 'sync':
            with self.operation_lock:
                return self.sync()
        elif d['type'] == 'setpass':
            with self.operation_lock:
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
        elif d['type'] == 'ping':
            return {'pong': True}
        elif d['type'] == 'fotoadmin-scan-userdirs':
            return self.cilia.send(d)
        elif d['type'] == 'fotoadmin-move-fotos':
            with self.operation_lock:
                ret = self.daan.send(d)
                if 'success' not in ret:
                    return ret
                ret = scan_fotos()
                if 'success' not in ret:
                    return ret
                return self.cilia.send({
                    'type': 'fotoadmin-remove-moved-fotos',
                    'store': d['store'],
                    'user': d['user'],
                    'dir': d['dir']})
        elif d['type'] == 'fotoadmin-scan-fotos':
            with self.operation_lock:
                return scan_fotos()
        elif d['type'] == 'openvpn_create':
            with self.operation_lock:
                # XXX hoeft niet onder de operation_lock?
                u = Es.by_name(d['user'])
                if u is None:
                    return {'error': 'no such user'}
                u = u.as_user()
                if d['want'] == 'exe':
                    create_openvpn_installer(self, u)
                else:
                    create_openvpn_zip(self, u)
        elif d['type'] == 'update-site-agenda':
            with self.operation_lock:
                return update_site_agenda(self)
        elif d['type'] in ['fotoadmin-create-event']:
            with self.operation_lock:
                return self.daan.send(d)
        elif d['type'] == 'last-synced?':
            return self.last_sync_ts
        elif d['type'] in ('fin-get-account', 'fin-get-debitors'):
            return self.moniek.send(d)
        else:
            logging.warn("Unknown command: %s" % d['type'])

# vim: et:sta:bs=2:sw=4:
