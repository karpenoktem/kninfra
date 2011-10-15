import _import

from datetime import datetime
from kn.leden.sessions import scol

scol.remove({'expire_dt': {'$lt': datetime.now()}})
