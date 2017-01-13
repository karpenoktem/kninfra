import _import # noqa: F401

# WARNING
# Please make very sure that this script is up-to-date.  It is a crime
# to leak private data entrusted to us.

from kn.base.conf import from_settings_import
from_settings_import("DT_MIN", "DT_MAX", globals())
from kn.leden.mongo import db

import bson
import zipfile

import datetime
import pprint

print 'entities'
with open('entities.bsons', 'w') as f:
    for e in db.entities.find():
        if 'telephones' in e:
            for t in e['telephones']:
                t['number'] = '<private>'
        if 'studies' in e:
            for s in e['studies']:
                if 'number' in s:
                    del s['number']
        if 'addresses' in e:
            e['addresses'] = [
                    {'city': '<private>',
                     'street': '<private>',
                     'zip': '<private>',
                     'number': '<private>',
                     'from': DT_MIN,
                     'until': DT_MAX}]
        if 'emailAddresses' in e and 'names' in e and e['names']:
            e['emailAddresses'] = [
                    {'from': DT_MIN,
                     'until': DT_MAX,
                     'email': e['names'][0] + '@kn.cx'}]
        if 'password' in e:
            e['password'] = None
        if 'temp' in e:
            del e['temp']
        f.write(bson.BSON.encode(e))
        #pprint.pprint(e)

print 'relations'
with open('relations.bsons', 'w') as f:
    for r in db.relations.find():
        f.write(bson.BSON.encode(r))

print 'events'
with open('events.bsons', 'w') as f:
    for r in db.events.find():
        f.write(bson.BSON.encode(r))

# vim: et:sta:bs=2:sw=4:
