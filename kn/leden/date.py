# vim: et:sta:bs=2:sw=4:
import datetime
import time
import threading

def now():
    return sclock.now

class Clock(threading.Thread):
    def __init__(self, interval):
        super(Clock,self).__init__()
        self.interval = interval
        self.now = datetime.datetime.now()
        self.daemon = True
        # ^ Prevents this thread from keeping the program alive.

    def run(self):
        while(True):
            time.sleep(self.interval)
            self.now = datetime.datetime.now()

sclock = Clock(1)
sclock.start()

def date_to_dt(d):
    return datetime.datetime.combine(d, datetime.time())
