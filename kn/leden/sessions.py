import datetime

from django.contrib.sessions.backends.base import SessionBase, CreateError
from django.utils.encoding import force_unicode

from kn.leden.mongo import db

scol = db['sessions']


class SessionStore(SessionBase):
    def __init__(self, session_key=None):
        super(SessionStore, self).__init__(session_key)

    def load(self):
        s = scol.find_one({'_id': self.session_key,
              'expire_dt': {
                  '$gt': datetime.datetime.now()}})
        if s is None:
            self.create()
            return {}
        return self.decode(force_unicode(s['data']))

    def exists(self, session_key):
        return scol.find_one({'_id': session_key}) is not None

    def create(self):
        while True:
            self._session_key = self._get_new_session_key()
            try:
                self.save(must_create=True)
            except CreateError:
                continue
            self.modified = True
            self._session_cache = {}
            return

    def save(self, must_create=False):
        n = {'_id': self.session_key,
            'data': self.encode(self._get_session(
                    no_load=must_create)),
            'expire_dt': self.get_expiry_date()}
        scol.update({'_id': self.session_key}, n, True)
        # TODO handle errors

    def delete(self, session_key=None):
        if session_key is None:
            if self.session_key is None:
                return
            session_key = self.session_key
        scol.remove({'_id': session_key})


def ensure_indices():
    scol.ensure_index('expire_dt')

# vim: et:sta:bs=2:sw=4:
