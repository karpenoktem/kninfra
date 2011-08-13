import os.path
import logging
import socket
import select
import json
import os

""" Whim is a very simple server/client protocol.

    A client connects to the server and sends a JSON document.  The server
    handles that message and returns by sending a JSON document of its own.

    Whim is used internally by the sync daemons Giedo, Daan and Cilia """


class WhimClient(object):
        def __init__(self, address, family='unix'):
                if family == 'tcp':
                        sf = socket.AF_INET
                elif family == 'unix':
                        sf = socket.AF_UNIX
                else:
                        raise ValueError, 'unknown family'
                self.s = socket.socket(sf, socket.SOCK_STREAM)
                self.s.connect(address)
                self.f = self.s.makefile()
        def send(self, d):
                self.f.write(json.dumps(d))
                self.f.write("\n")
                self.f.flush()
                return json.loads(self.f.readline())

class WhimDaemon(object):
        def __init__(self, address, family='unix'):
                self.sockets = []
                self.address = address
                self.family = family
                self.sock_to_file = dict()
                self.ls = None

        def pre_mainloop(self):
                pass

        def run(self):
                if self.family == 'tcp':
                        sf = socket.AF_INET
                elif self.family == 'unix':
                        sf = socket.AF_UNIX
                else:
                        raise ValueError, 'unknown family'
                ls = self.ls = socket.socket(sf, socket.SOCK_STREAM)
                if self.family == 'unix':
                        if os.path.exists(self.address):
                                os.unlink(self.address)
                ls.bind(self.address)
                if self.family == 'unix':
                        os.chmod(self.address, 0600)
                self.pre_mainloop()
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
                                self.sock_to_file[s].write(json.dumps(ret))
                                self.sock_to_file[s].write("\n")
                                self.sock_to_file[s].flush()
                except Exception, e:
                        logging.exception("Uncaught exception")

        def handle(self, d):
                raise NotImplementedError
