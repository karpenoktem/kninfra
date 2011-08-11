import os.path
import logging
import socket
import select
import json
import os

class UnixJSONDaemon(object):
        """ Simple synchronous daemon that listens on a UNIX socket for
            JSON objects.  Used by the Giedo and Daan daemons."""
        def __init__(self, path):
                self.sockets = []
                self.path = path
                self.sock_to_file = dict()
                self.ls = None

        def run(self):
                ls = self.ls = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                if os.path.exists(self.path):
                        os.unlink(self.path)
                ls.bind(self.path)
                os.chmod(self.path, 0600)
                ls.listen(8)
                while True:
                        rs, ws, xs = select.select(self.sockets + [ls], [], [])
                        if ls in rs:
                                s, addr = ls.accept()
                                self.sockets.append(s)
                                self.sock_to_file[s] = s.makefile()
                                rs.remove(ls)
                        for s in rs:
                                # NOTE This might block. We assume our client is
                                #      not mischievous.
                                self.handle_socket(s)

        def handle_socket(self, s):
                try:
                        raw = self.sock_to_file[s].readline().strip()
                        if not raw:
                                self.sockets.remove(s)
                                del self.sock_to_file[s]
                        else:
                                d = json.loads(raw)
                                self.handle(d)
                except Exception, e:
                        logging.exception("Uncaught exception")

        def handle(self, d):
                raise NotImplementedError
