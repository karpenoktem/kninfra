import datetime

# TODO Cache this in a proper way
def now():
        return datetime.datetime.now()

def date_to_dt(d):
        return datetime.datetime.combine(d, datetime.time())
