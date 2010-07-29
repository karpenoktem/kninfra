import pymongo
from kn.settings import MONGO_DB, MONGO_HOST

conn = pymongo.Connection(MONGO_HOST)
db = conn[MONGO_DB]
