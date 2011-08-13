import os.path
import logging
import socket
import select
import json
import os

class JSONDaemon(object):
        """ Simple synchronous daemon that  for
            JSON objects.  Used by the Giedo and Daan daemons."""
        def __init__(self, address, family='unix'):
                self.sockets = []
                self.address = address
                self.family = family
                self.sock_to_file = dict()
                self.ls = None

        def run(self):
                if self.family == 'tcp':
                        sf = socket.AF_INET
                elif self.family == 'unix':
                        sf = socket.AF_UNIX
                else:
                        raise ValueError, 'unknown family'
                ls = self.ls = socket.socket(sf, socket.SOCK_STREAM)
                if sf == 'unix':
                        if os.path.exists(self.address):
                                os.unlink(self.address)
                ls.bind(self.address)
                if sf == 'unix':
                        os.chmod(self.address, 0600)
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
                                ret = self.handle(d)
                                if ret is not None:
                                        self.sock_to_file[s].write(
                                                        json.dumps(ret))
                                        self.sock_to_file[s].write("\n")
                except Exception, e:
                        logging.exception("Uncaught exception")

        def handle(self, d):
                raise NotImplementedError
