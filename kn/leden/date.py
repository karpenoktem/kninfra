# vim: et:sta:bs=2:sw=4:
import datetime
import time

def now():
    return datetime.datetime.now()

def date_to_dt(d):
    return datetime.datetime.combine(d, datetime.time())

def date_to_midnight(d):
    return datetime.datetime(d.year, d.month, d.day)

