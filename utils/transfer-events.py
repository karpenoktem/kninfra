import _import

import kn.leden.mongo

import pprint

ecol = kn.leden.mongo.db['events']
scol = kn.leden.mongo.db['event_subscriptions']
e2col = kn.leden.mongo.db['events2']

new_events = []

for e in ecol.find():
    old_subscriptions = []
    for s in scol.find({'event': e['_id']}):
        old_subscriptions.append(s)

    new_events.append({
            '_id': e['_id'],
            'name': e['name'],
            'humanName': e['humanName']})

for d in new_events:
    e2col.save(d)

# vim: et:sta:bs=2:sw=4:
