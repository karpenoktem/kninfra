import threading
import os.path
import logging
import socket
import select
import os

import msgpack
import mirte

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
        self.w_lock = threading.Lock()
        self.n_send_lock = threading.Lock()
        self.n_send = 0
        self.lock = threading.Lock()
        self.packer = msgpack.Packer()
        self.unpacker = msgpack.Unpacker()
        self.event_lut = {}
        self.msg_lut = {}
        self.got_reader = False
    def send(self, d):
        """ Sends the message @d to the server and returns its
            response """
        # Get a message id by incrementing self.n_send and set
        # a event in place.
        event = threading.Event()
        with self.n_send_lock:
            n = self.n_send
            self.n_send += 1
        with self.lock:
            self.event_lut[n] = event
        # Pack the message
        bs = self.packer.pack((n, d))
        # Send the message
        with self.w_lock:
            self.f.write(bs)
            self.f.flush()
        while True:
            with self.lock:
                # Has the message been received by another
                # thread that is the reader.
                if n in self.msg_lut:
                    ret = self.msg_lut[n]
                    del self.msg_lut[n]
                    del self.event_lut[n]
                    return ret
                # Is there another thread reading the socket?
                if not self.got_reader:
                    # No: read ourselves.
                    self.got_reader = True
                    break
            event.wait()
        # We are the reader now
        got_own_message = False
        own_message = None
        while not got_own_message:
            bits = self.s.recv(4096)
            if not bits:
                raise IOError, "No data"
            self.unpacker.feed(bits)
            for raw_msg in self.unpacker:
                mid, msg = raw_msg
                # Is this our message?
                if mid == n:
                    got_own_message = True
                    own_message = msg
                    continue
                # This is another thread's message
                with self.lock:
                    self.msg_lut[mid] = msg
                self.event_lut[mid].set()
        # We got our message, but first check whether we need to
        # pass control to another reader
        with self.lock:
            self.got_reader = False
            del self.event_lut[n]
            if self.event_lut:
                mid = next(iter(self.event_lut))
                self.event_lut[mid].set()
        return own_message


class WhimDaemon(object):
    def __init__(self, address, family='unix'):
        self.threadPool = mirte.get_a_manager().get_a('threadPool')
        self.sockets = set()
        self.address = address
        self.family = family
        self.sock_state = dict()
        self.ls = None
        self.packer = msgpack.Packer()

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
            rs, ws, xs = select.select(list(self.sockets) + [ls],
                    [], [])
            if ls in rs:
                s, addr = ls.accept()
                self.sockets.add(s)
                self.sock_state[s] = (s.makefile(),
                              msgpack.Unpacker(),
                              threading.Lock())
                rs.remove(ls)
            for s in rs:
                self.handle_socket(s)

    def handle_socket(self, s):
        f, unp, wl = self.sock_state[s]
        bits = s.recv(4096)
        if not bits:
            logging.info("closed socket")
            f.close()
            s.close()
            self.sockets.remove(s)
            del self.sock_state[s]
            return
        unp.feed(bits)
        for raw_msg in unp:
            mid, msg = raw_msg
            self.threadPool.execute(self.__handle, mid, msg, s)

    def __handle(self, mid, msg, s):
        f, unp, wl = self.sock_state[s]
        ret = self.handle(msg)
        with wl:
            f.write(self.packer.pack([mid, ret]))
            f.flush()

    def handle(self, d):
        raise NotImplementedError

# vim: et:sta:bs=2:sw=4:
