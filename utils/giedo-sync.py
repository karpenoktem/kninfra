#!/usr/bin/env python
import _import  # noqa: F401

import grpc
import protobufs.messages.common_pb2 as common_pb2
import protobufs.messages.giedo_pb2_grpc as giedo_pb2_grpc

from django.conf import settings

giedo = giedo_pb2_grpc.GiedoStub(
    grpc.insecure_channel('unix:' + settings.GIEDO_SOCKET))
giedo.SyncBlocking(common_pb2.Empty())
