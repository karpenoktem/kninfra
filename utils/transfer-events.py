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
        state = 0
        type_ = 'subscribed'
        by = None
        if old.get('confirmed') == False:
            state = 2
            type_ = 'invited'
            by = old.get('subscribedBy')

        changes = [{
            'type': type_,
            'when': old.get('date'),
            'notes': old.get('userNotes'),
            'by': old.get('subscribedBy')
        }]

        if old.get('dateConfirmed'):
            changes.append({
                'type': 'confirmed',
                'when': old.get('dateConfirmed'),
                'notes': None,
                'by': old.get('user')
            })

        new_subscription = {
            'who': old['user'],
            'state': state,
            'when': old.get('date'),
            'debit': old.get('debit'),
            'changes': changes
        }

        new_subscriptions.append(new_subscription)
            

    new_event = {
        '_id': e.get('_id'),
        'name': e.get('name'),
        'humanName': e.get('humanName'),
        'owner': e.get('owner'),
        'cost': e.get('cost'),
        'when': e.get('date'),
        'description': e.get('description'),
        'description_html': e.get('description_html', escape(e.get('description'))),
        'manually_closed': not e.get('is_open'),
        'has_public_subscriptions': e.get('has_public_subscriptions', False),
        'owner_can_subscribe_others': True,
        'anyone_can_subscribe_others': e.get('everyone_can_subscribe_others', False),
        'msg_subscribed': e.get('mailBody'),
        'msg_subscribedBy': e.get('subscribedByOtherMailBody'),
        'msg_confirmed': e.get('confirmationMailBody'),
        'is_official': e.get('is_official'),
        'subscriptions': new_subscriptions,
        'changes': [{
            'type': 'created',
            'when': None, # Is niet bekend :(
            'by': e.get('createdBy')
        }]
    }

    new_events.append(new_event)

for d in new_events:
    e2col.save(d)

# vim: et:sta:bs=2:sw=4:
