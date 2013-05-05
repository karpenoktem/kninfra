import _import
import kn.leden.mongo
import pprint
from django.utils.html import escape

ecol = kn.leden.mongo.db['events']
scol = kn.leden.mongo.db['event_subscriptions']
e2col = kn.leden.mongo.db['events2']

new_events = []

for e in ecol.find():
    old_subscriptions = []
    for s in scol.find({'event': e['_id']}):
        old_subscriptions.append(s)

    #pprint.pprint(e)
    
    new_subscriptions = []
    for old in old_subscriptions:
        state = 1;
        type_ = 'subscribed'
        by = None
        if old.get('confirmed') == False:
            state = 2
            type_ = 'subscribedBy'
            by = old.get('subscribedBy')

        changes = [{
            'type': type_,
            'when': old.get('date'),
            'notes': old.get('userNotes')
        }]

        if old.get('dateConfirmed'):
            changes.append({
                'type': 'confirmed',
                'when': old.get('dateConfrmed'),
                'notes': None
            })

        new_subscription = {
            'who': old['user'],
            'state': state,
            'when': old.get('date'),
            'debit': old.get('debit'),
            'by': by,
            'changes': changes
        }

        new_subscriptions.append(new_subscription)
            

    new_event = {
        '_id': e['_id'],
        'name': e['name'],
        'humanName': e['humanName'],
        'owner': e['owner'],
        'cost': e['cost'],
        'description': e['description'],
        'manually_closed': not e['is_open'],
        'owner_can_subscribe_others': True,
        'msg_subscribed': e['mailBody'],
        'msg_subscribedBy': e.get('subscribedByOtherMailBody'),
        'msg_confirmed': e.get('everyone_can_subscribe_others'),
        'is_official': e.get('is_official'),
        'subscriptions': new_subscriptions,
        'changes': [{
            'type': 'created',
            'when': None, # Is niet bekend :(
            'by': e.get('createdBy')
        }]
    }
    try:
        new_event['description_html'] = e['description_html']
    except KeyError:
        new_event['description_html'] = escape(e['description'])

    try:
        new_event['when'] = e['date']
    except KeyError:
        new_event['when'] = None

    try:
        new_event['has_public_subscriptions'] = e['has_public_subscriptions']
    except KeyError:
        new_event['has_public_subscriptions'] = False

    try:
        new_event['anyone_can_subscribe_others'] = e['everyone_can_subscribe_others']
    except KeyError:
        new_event['heveryone_can_subscribe_others'] = False

    new_events.append(new_event)

for d in new_events:
    e2col.save(d)

# vim: et:sta:bs=2:sw=4:
