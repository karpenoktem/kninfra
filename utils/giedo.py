# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import logging
import time
from concurrent import futures

import grpc
import protobufs.messages.giedo_pb2_grpc as giedo_pb2_grpc
import sdnotify

from django.conf import settings

from kn.utils.giedo.service import Giedo

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(relativeCreated)d %(levelname)-8s%(name)s:%(message)s"
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    giedo_pb2_grpc.add_GiedoServicer_to_server(Giedo(), server)
    server.add_insecure_port('unix:' + settings.GIEDO_SOCKET)
    server.start()
    sdnotify.SystemdNotifier().notify("READY=1")
    while True:
        # Sleep forever.
        time.sleep(60 * 60 * 24)
