#!/usr/bin/env python
# vim: et:sta:bs=2:sw=4:
# this file should retain python2 compatibility until Hans is ported to python3
import _import  # noqa: F401

import protobufs.messages.hans_pb2_grpc as hans_pb2_grpc

from django.conf import settings

from kn.utils.hans.service import Hans
from microservice import Microservice

class HansD(Microservice):
    def __init__(self):
        super(HansD, self).__init__()
        hans_pb2_grpc.add_HansServicer_to_server(Hans(), self.server)
        self.start(settings.HANS_SOCKET)

if __name__ == '__main__':
    HansD()
