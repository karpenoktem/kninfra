import datetime


def now() -> datetime.datetime:
    return datetime.datetime.now()


def date_to_dt(d: datetime.date) -> datetime.datetime:
    return datetime.datetime.combine(d, datetime.time())


def date_to_midnight(d: datetime.date) -> datetime.datetime:
    return datetime.datetime(d.year, d.month, d.day)

# vim: et:sta:bs=2:sw=4:
