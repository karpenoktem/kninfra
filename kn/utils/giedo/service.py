import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import grpc
import protobufs.messages.common_pb2 as common_pb2
import protobufs.messages.daan_pb2 as daan_pb2
import protobufs.messages.daan_pb2_grpc as daan_pb2_grpc
import protobufs.messages.giedo_pb2 as giedo_pb2
import protobufs.messages.giedo_pb2_grpc as giedo_pb2_grpc
import protobufs.messages.hans_pb2_grpc as hans_pb2_grpc

from django.conf import settings

import kn.leden.entities as Es
from kn.utils.giedo._ldap import generate_ldap_changes
from kn.utils.giedo.db import update_db
from kn.utils.giedo.fotos import scan_fotos
from kn.utils.giedo.mailman import generate_mailman_changes
from kn.utils.giedo.postfix import (generate_postfix_map,
                                    generate_postfix_slm_map)
from kn.utils.giedo.siteagenda import update_site_agenda
from kn.utils.giedo.unix import generate_unix_map
from kn.utils.giedo.wolk import generate_wolk_changes
from kn.utils.whim import WhimClient

class Giedo(giedo_pb2_grpc.GiedoServicer):

    def __init__(self):
        super(Giedo, self).__init__()
        self.log = logging.getLogger('giedo')
        self.last_sync_ts = 0
        self.daan, self.hans = None, None
        try:
            self.daan = daan_pb2_grpc.DaanStub(
                grpc.insecure_channel('unix:' + settings.DAAN_SOCKET))
        except Exception:
            self.log.exception("Couldn't connect to daan")
        try:
            self.hans = hans_pb2_grpc.HansStub(
                grpc.insecure_channel('unix:' + settings.HANS_SOCKET))
        except Exception:
            self.log.exception("Couldn't connect to hans")
        self.threadPool = ThreadPoolExecutor(max_workers=4)
        self.operation_lock = threading.Lock()
        self.ss_actions = (
            ('postfix', self.daan.SetPostfixMap, self._gen_postfix),
            ('postfix-slm', self.daan.SetPostfixSenderLoginMap, self._gen_postfix_slm),
            ('mailman', self.hans.ApplyChanges, self._gen_mailman),
            ('ldap', self.daan.ApplyLDAPChanges, self._gen_ldap)
        )

    def _gen_wolk(self):
        return {'type': 'wolk',
                'changes': generate_wolk_changes(self)}

    def _gen_ldap(self):
        return generate_ldap_changes()

    def _gen_postfix_slm(self):
        return generate_postfix_slm_map()

    def _gen_postfix(self):
        return generate_postfix_map()

    def _gen_mailman(self):
        return generate_mailman_changes(self.hans)

    def _gen_unix(self):
        return {'type': 'unix',
                'map': generate_unix_map(self)}

    def sync(self):
        logging.info("what are you syncing about?")
        update_db_start = time.time()
        update_db(self)
        logging.info("update_db %s" % (time.time() - update_db_start))
        todo = [len(self.ss_actions)]
        todo_lock = threading.Lock()
        todo_event = threading.Event()

        def _sync_action(func, name, daemon, action):
            try:
                func(name, daemon, action)
            except Exception:
                logging.exception('uncaught exception in %s (daemon %s)' %
                                  (name, daemon))
            with todo_lock:
                todo[0] -= 1
                if todo[0] == 0:
                    todo_event.set()

        def _entry(name, send, action):
            start = time.time()
            msg = action()
            elapsed = time.time() - start
            logging.info("generate %s %.4f" % (name, elapsed))
            start = time.time()
            send(msg)
            elapsed = time.time() - start
            logging.info("send %s %.4f (%s to go)" %
                         (name, elapsed, todo[0] - 1))

        for action in self.ss_actions:
            self.threadPool.submit(_sync_action, _entry, *action)
        todo_event.wait()
        self.last_sync_ts = time.time()

    def sync_locked(self):
        with self.operation_lock:
            self.sync()

    def SyncBlocking(self, request, context):
        self.sync_locked()
        return common_pb2.Empty()

    def SyncAsync(self, request, context):
        self.threadPool.submit(self.sync_locked)
        return common_pb2.Empty()

    def LastSynced(self, request, context):
        return giedo_pb2.LastSyncedResult(time=self.last_sync_ts)

    def SetPassword(self, request, context):
        with self.operation_lock:
            u = Es.by_name(request.user)
            if u is None:
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('no such user')
                return common_pb2.Empty()
            u = u.as_user()
            if not u.check_password(request.oldpass):
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                context.set_details('wrong old password')
                return common_pb2.Empty()
            u.set_password(request.newpass)
            self.daan.SetLDAPPassword(daan_pb2.LDAPNewPassword(
                user=request.user.encode(),
                password=request.newpass.encode()))
        return common_pb2.Empty()

    def FotoadminCreateEvent(self, request, context):
        with self.operation_lock:
            try:
                self.daan.FotoadminCreateEvent(request)
            except grpc.RpcError as e:
                context.set_code(e.code())
                context.set_details(e.details())
        return common_pb2.Empty()

    def ScanFotos(self, request, context):
        with self.operation_lock:
            scan_fotos()
        return common_pb2.Empty()

    def UpdateSiteAgenda(self, request, context):
        with self.operation_lock:
            ret = update_site_agenda()
            if 'success' not in ret:
                context.set_code(grpc.StatusCode.UNKNOWN)
                context.set_details(ret['error'])
        return common_pb2.Empty()

# vim: et:sta:bs=2:sw=4:
