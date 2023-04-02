# vim: et:sta:bs=2:sw=4:
import threading

import protobufs.messages.common_pb2 as common_pb2
import protobufs.messages.daan_pb2_grpc as daan_pb2_grpc

from kn.utils.daan.postfix import set_postfix_map, set_postfix_slm_map


class Daan(daan_pb2_grpc.DaanServicer):

    def __init__(self):
        super(Daan, self).__init__()
        self.postfix_lock = threading.Lock()
        self.postfix_slm_lock = threading.Lock()

    def SetPostfixMap(self, request, context):
        with self.postfix_lock:
            set_postfix_map(request.map)
        return common_pb2.Empty()

    def SetPostfixSenderLoginMap(self, request, context):
        with self.postfix_slm_lock:
            set_postfix_slm_map(request.map)
        return common_pb2.Empty()
