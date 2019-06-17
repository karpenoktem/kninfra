# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import logging
import os
import time
from concurrent import futures

import grpc
import protobufs.messages.daan_pb2_grpc as daan_pb2_grpc
import sdnotify

from django.conf import settings

from kn.utils.daan.service import Daan

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(relativeCreated)d %(levelname)-8s%(name)s:%(message)s"
    )
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    daan_pb2_grpc.add_DaanServicer_to_server(Daan(), server)
    server.add_insecure_port('unix:' + settings.DAAN_SOCKET)
    server.start()
    os.chown(settings.DAAN_SOCKET, settings.INFRA_UID, -1)
    sdnotify.SystemdNotifier().notify("READY=1")
    while True:
        # Sleep forever.
        time.sleep(60 * 60 * 24)
