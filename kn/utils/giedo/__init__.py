# vim: et:sta:bs=2:sw=4:
import threading
import os.path
import logging
import socket
import select
import time
import json
import os
import subprocess
import urllib2
import itertools
from urllib import urlencode
from M2Crypto import RSA
from kn.base._random import pseudo_randstr

from django.core.files.storage import default_storage

import mirte # github.com/bwesterb/mirte

import kn.leden.entities as Es

from kn.utils.whim import WhimDaemon, WhimClient
from kn.leden.date import now

from kn import settings

from kn.utils.giedo.db import update_db
from kn.utils.giedo.postfix import generate_postfix_map
from kn.utils.giedo.mailman import generate_mailman_changes
from kn.utils.giedo.wiki import generate_wiki_changes
from kn.utils.giedo.forum import generate_forum_changes
from kn.utils.giedo.unix import generate_unix_map
from kn.utils.giedo.openvpn import create_openvpn_installer, create_openvpn_zip
from kn.utils.giedo.siteagenda import update_site_agenda

class Giedo(WhimDaemon):
    def __init__(self):
        super(Giedo, self).__init__(settings.GIEDO_SOCKET)
        self.daan = WhimClient(settings.DAAN_SOCKET)
        self.cilia = WhimClient(settings.CILIA_SOCKET)
        self.mirte = mirte.get_a_manager()
        self.threadPool = self.mirte.get_a('threadPool')
        self.operation_lock = threading.Lock()
        self.push_changes_event = threading.Event()
        self.threadPool.execute(self.run_change_pusher)
        if default_storage.exists("villanet.pem"):
            self.villanet_key = RSA.load_pub_key(default_storage.path(
                "villanet.pem"))
        self.ss_actions = (
                  ('postfix', self.daan, self._gen_postfix),
                  ('mailman', self.daan, self._gen_mailman),
                  ('forum', self.daan, self._gen_forum),
                  ('unix', self.cilia, self._gen_unix),
                  ('wiki', self.daan, self._gen_wiki))
        self.push_changes_event.set()


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

    def _sync_villanet(self):
        ret = self.villanet_request({'action': 'listUsers'})
        if not ret[0]:
            return
        ret = json.loads(ret[1])
        users = dict()
        ulut = dict()
        for u in Es.users():
            ulut[u._id] = str(u.name)
        member_relations = itertools.groupby(Es.query_relations(
            _with=Es.by_name('leden'), until=now()), lambda x: x['who'])
        for user_id, relations in member_relations:
            latest = max(relations, key=lambda x: x['until'])
            users[ulut[user_id]] = latest['until'].strftime('%Y-%m-%d')
        vn = set(ret.keys())
        kn = set(users.keys())
        dt_max = settings.DT_MAX.strftime('%Y-%m-%d')
        for name in kn - vn:
            data = {
                    'username': name,
                    'password': self.villanet_encrypt_password(
                        pseudo_randstr(16)),
                }
            if users[name] != dt_max:
                data['till'] = users[name]
            pc = Es.PushChange({'system': 'villanet', 'action': 'addUser',
                'data': data})
            pc.save()
        for name in vn - kn:
            logging.info("Stray user %s" % name)
        for name in vn & kn:
            remote = (ret[name]['till'][:10] if ret[name]['till'] is not None
                    else '')
            local = users[name] if users[name] != dt_max else ''
            if remote != local:
                pc = Es.PushChange({'system': 'villanet',
                    'action': 'changeUser', 'data': {
                        'username': name,
                        'till': local
                        }})
                pc.save()
        self.push_changes_event.set()

    def sync(self):
        update_db_start = time.time()
        update_db(self)
        logging.info("update_db %s" % (time.time() - update_db_start))
        todo = [len(self.ss_actions)]
        todo_lock = threading.Lock()
        todo_event = threading.Event()

        def _sync_action(func, *args):
            func(*args)
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

        todo[0] += 1
        self.threadPool.execute(_sync_action, self._sync_villanet)
        for act in self.ss_actions:
            self.threadPool.execute(_sync_action, _entry, *act)
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
                pc = Es.PushChange({'system': 'villanet',
                    'action': 'changeUser', 'data': {
                        'username': d['user'],
                        'password': self.villanet_encrypt_password(d['newpass'])
                            }})
                pc.save()
                self.push_changes_event.set()
                d2 = {'type': 'setpass',
                      'user': d['user'],
                      'pass': d['newpass']}
                self.daan.send(d2)
                self.cilia.send(d2)
                return {'success': True}
            elif d['type'] == 'fotoadmin-move-fotos':
                # TODO should this block Giedo?
                ret = self.daan.send(d)
                if 'success' not in ret:
                    return ret
                return self.cilia.send({
                    'type': 'fotoadmin-remove-moved-fotos',
                    'user': d['user'],
                    'dir': d['dir']})
            elif d['type'] == 'openvpn_create':
                # XXX hoeft niet onder de operation_lock
                u = Es.by_name(d['user'])
                if u is None:
                    return {'error': 'no such user'}
                u = u.as_user()
                if d['want'] == 'exe':
                    create_openvpn_installer(self, u)
                else:
                    create_openvpn_zip(self, u)
            elif d['type'] == 'update-site-agenda':
                return update_site_agenda(self)
            elif d['type'] in ['update-knsite', 'update-knfotos',
                    'fotoadmin-create-event']:
                return self.daan.send(d)
            else:
                logging.warn("Unknown command: %s" % d['type'])

    def villanet_encrypt_password(self, password):
        ctx = self.villanet_key.public_encrypt(password, RSA.pkcs1_padding)
        return ctx.encode('base64').replace("\n", '')

    def run_change_pusher(self):
        while True:
            self.push_changes_event.wait()
            for pc in Es.pcol.find():
                if pc['system'] == 'villanet':
                    if settings.VILLANET_SECRET_API_KEY == '':
                        logging.warn("VILLANET_SECRET_API_KEY not set")
                        continue
                    params = pc['data']
                    params['action'] = pc['action']
                    ret = self.villanet_request(params)
                    if not ret[0]:
                        continue
                else:
                    logging.warn("Unknown PushChange system %s " % pc['system'])
                Es.pcol.remove({'_id': pc['_id']})

    def villanet_request(self, params):
        params['apikey'] = settings.VILLANET_SECRET_API_KEY
        url = "http://www.vvs-nijmegen.nl/knapi.php?"+ urlencode(params)
        ret = urllib2.urlopen(url).read()
        ret = ret.strip()
        if ret[:4] == 'OK: ':
            return (True, ret[4:])
        else:
            return (False, ret)
