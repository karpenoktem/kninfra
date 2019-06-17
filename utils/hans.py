# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import logging
import time
from concurrent import futures

import grpc
import protobufs.messages.hans_pb2_grpc as hans_pb2_grpc
import sdnotify

from django.conf import settings

from kn.utils.hans.service import Hans

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(relativeCreated)d %(levelname)-8s%(name)s:%(message)s"
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    hans_pb2_grpc.add_HansServicer_to_server(Hans(), server)
    server.add_insecure_port('unix:' + settings.HANS_SOCKET)
    server.start()
    sdnotify.SystemdNotifier().notify("READY=1")
    while True:
        # Sleep forever.
        time.sleep(60 * 60 * 24)
