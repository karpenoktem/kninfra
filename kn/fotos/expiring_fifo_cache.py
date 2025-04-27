import datetime
import collections

class ExpiringFifoCache(object):
    def __init__(self, wrapped, size=512, time=datetime.timedelta(hours=1)):
        self._size = size
        self._time = time
        self.__wrapped__ = wrapped
        self._cache = {}
        self._q = collections.deque()

    def insert(self, key, val):
        now = datetime.datetime.now()
        self._cache[key] = val
        self._q.append((now, key))

    def check_prune(self):
        while len(self._q) > self._size or (len(self._q) > 0 and not self.is_valid(self._q[0][0])):
            insert_date, key = self._q.popleft()
            del self._cache[key]
                
    def is_valid(self, insert_date):
        now = datetime.datetime.now()
        # check that date is in the past but not too far
        return (now - insert_date < self._time) and insert_date < now

    def __len__(self):
        return len(self._q)

    def __call__(self, *args):
        now = datetime.datetime.now()
        n = None
        self.check_prune()
        try:
            n = self._cache[args]
            return n
        except KeyError:
            n = self.__wrapped__(*args)
            self.insert(args, n)
            return n
