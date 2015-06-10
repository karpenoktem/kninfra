import _import

from kn.leden.mongo import db, _id

ecol = db['events']
scol = db['event_subscriptions']

def main():
    '''
    Update the database to use more modern subscription system.
    WARNING: this throws away the 'debit' fields.
    WARNING: make a backup first! It is hard to roll back these changes.
    '''
    events = ecol.find().sort('date')
    ecount = 0
    scount = 0
    for event in events:
        ecount += 1
        print 'Event:', event.get('name')
        subscriptions = event.get('subscriptions', [])
        users = {s['user'] for s in subscriptions}
        for subscription in scol.find({'event': event['_id']}):
            scount += 1
            print subscription # DEBUG TODO
            if subscription['user'] in users:
                raise ValueError('user already in set')
            users.add(subscription['user'])
            subscription2 = {
                'user': subscription['user']
            }
            if 'subscribedBy' in subscription:
                subscription2['inviter'] = subscription['subscribedBy']
                subscription2['inviterNotes'] = subscription['subscribedBy_notes']
                subscription2['inviteDate'] = subscription['date']
                if 'dateConfirmed' in subscription:
                    subscription2['history'] = [{
                        'state': 'subscribed',
                        'date': subscription['dateConfirmed'],
                    }]
            else:
                subscription2['history'] = [{
                    'state': 'subscribed',
                    'date': subscription['date'],
                }]
            if 'userNotes' in subscription:
                subscription2['history'][0]['notes'] = subscription['userNotes']
            subscriptions.append(subscription2)
        ecol.update({'_id': event['_id']}, {'$set': {'subscriptions': subscriptions}})
        scol.remove({'event': event['_id']})
    print 'Moved %d subscriptions into %d events.' % (scount, ecount)

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
