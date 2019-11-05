#!/usr/bin/env python
# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import logging
import time
from concurrent import futures

import protobufs.messages.giedo_pb2_grpc as giedo_pb2_grpc

from django.conf import settings

from kn.utils.giedo.service import Giedo
from microservice import Microservice

class GiedoD(Microservice):
    def __init__(self):
        super().__init__()
        giedo_pb2_grpc.add_GiedoServicer_to_server(Giedo(), self.server)
        self.start(settings.GIEDO_SOCKET)

if __name__ == '__main__':
    GiedoD()
