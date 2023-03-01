#!/usr/bin/env python
# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import protobufs.messages.daan_pb2_grpc as daan_pb2_grpc

from django.conf import settings

from kn.utils.daan.service import Daan
from microservice import Microservice

class DaanD(Microservice):
    def __init__(self):
        super().__init__()
        daan_pb2_grpc.add_DaanServicer_to_server(Daan(), self.server)
        self.start(settings.DAAN_SOCKET)

if __name__ == '__main__':
    DaanD()
