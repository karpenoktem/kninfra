# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401
import logging
import time
from concurrent import futures

import grpc
import sdnotify

from django.conf import settings

import ctypes, socket, os
from select import select 

def systemd_get_sockets():
    no_fds = int(os.getenv("LISTEN_FDS", "0"))
    return [socket.socket(fileno=fd) for fd in range(3, 3+no_fds)]

class TcpListenerWrapper(object):
    # https://github.com/grpc/grpc/blob/master/src/core/lib/iomgr/tcp_server_posix.cc#L575
    handleFun = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_void_p) 
    def __init__(self):
        self.pointer = ctypes.pointer((ctypes.c_size_t)())
    def __int__(self):
        # used by grpc to make the pointer type
        return ctypes.addressof(self.pointer)
    def handle(self, listen_fd, fd):
        # read the vtable..
        x = ctypes.cast(ctypes.c_void_p(self.pointer.contents.value+16), ctypes.POINTER(self.handleFun))
        x.contents(self.pointer, listen_fd, fd, ctypes.c_void_p())

class Microservice(object):
    def __init__(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(relativeCreated)d %(levelname)-8s%(name)s:%(message)s"
        )
        self.external_fd_listener = TcpListenerWrapper()
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=4), options={
            "external:systemd_socket": self.external_fd_listener
        }.items())

    def start(self, fallback_socket):
        sockets = systemd_get_sockets()
        if len(sockets) == 0:
           logging.info("falling back to unix socket")
           self.server.add_insecure_port('unix:' + fallback_socket)
        else:
           logging.info("listening on systemd managed socket")
           try:
               self.server.add_insecure_port('external:systemd_socket')
           except RuntimeError:
               print("ignoring error :)")
        self.server.start()
        for sock in sockets:
            sock.setblocking(False)
        sdnotify.SystemdNotifier().notify("READY=1")
        while True:
            readable, _, _ = select(sockets, [], [], 60*60*24)
            for sock in readable:
                #fd,addr = sock._accept()
                conn, addr = sock.accept()
                conn.setblocking(False)
                fd2 = os.dup(conn.fileno())
                self.external_fd_listener.handle(sock.fileno(), fd2)
