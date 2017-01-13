# vim: et:sta:bs=2:sw=4:
import _import # noqa: F401

from datetime import datetime
from kn.leden.sessions import scol

scol.remove({'expire_dt': {'$lt': datetime.now()}})
