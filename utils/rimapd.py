#!/usr/bin/env python
# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import csv
import os
import socket
import socketserver
import sys
import time
import sdnotify
import kn.leden.entities as Es

def systemd_get_sockets() -> list[socket.socket]:
    no_fds = int(os.getenv("LISTEN_FDS", "0"))
    return [socket.socket(fileno=fd) for fd in range(3, 3+no_fds)]

def check(username: str, password: str) -> bool:
    user = Es.by_name(username)
    # todo: dos opportunity?
    time.sleep(0.1)
    if user is None or not user.is_user \
       or not user.check_password(password):
        return False
    return True

class RImapHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.sendall(b"* OK\r\n")
        data = self.request.recv(1024)
        data = data.split(b'\r\n')[0].decode('utf-7')
        tag, cmd, *args = next(csv.reader([data], delimiter=' ', doublequote=False, escapechar='\\'))
        print("got login", tag, cmd, args[0])
        if cmd == 'LOGIN':
            user, password = args
            if check(user, password):
                self.request.sendall(tag.encode('utf7') + b" OK\r\n")
            else:
                self.request.sendall(tag.encode('utf7') + b" NO\r\n")

class SystemdTCPServer(socketserver.TCPServer):
    allow_reuse_address = True
    def __init__(self, conn, *args, **kwargs):
        if isinstance(conn, socket.socket):
            socketserver.BaseServer.__init__(self, conn, *args)
            self.socket = conn
        else:
            super().__init__(conn, *args, **kwargs)
    
if __name__ == "__main__":
    sockets = systemd_get_sockets()
    connection = None
    if len(sockets) == 0:
        connection = ()
        if len(sys.argv) == 3:
            connection = (sys.argv[1], int(sys.argv[2]))
            print("Listening on", connection)
        else:
            print("Usage:", sys.argv[0], "[host]", "[port]", file=sys.stderr)
            sys.exit(1)
    elif len(sockets) == 1:
        print("Listening on systemd-provided socket", file=sys.stderr)
        connection = sockets[0]
    else:
        print("Error: too many sockets passed by systemd", file=sys.stderr)
        sys.exit(1)
    with SystemdTCPServer(connection, RImapHandler) as server:
        sdnotify.SystemdNotifier().notify("READY=1")
        server.serve_forever()
