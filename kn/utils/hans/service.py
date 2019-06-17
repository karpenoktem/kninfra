from __future__ import absolute_import

import threading

import protobufs.messages.hans_pb2 as hans_pb2
import protobufs.messages.hans_pb2_grpc as hans_pb2_grpc

from kn.utils.hans.sync import maillist_apply_changes, maillist_get_membership


class Hans(hans_pb2_grpc.HansServicer):

    def __init__(self):
        super(Hans, self).__init__()
        self.mailman_lock = threading.Lock()

    def GetMembership(self, request, context):
        return maillist_get_membership()

    def ApplyChanges(self, request, context):
        with self.mailman_lock:
            maillist_apply_changes(request)
        return hans_pb2.ApplyChangesResp()

# vim: et:sta:bs=2:sw=4:
