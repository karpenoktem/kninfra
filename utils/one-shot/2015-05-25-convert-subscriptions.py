import _import  # noqa: F401

from kn.leden.mongo import db

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
        print('Event:', event.get('name'))
        if 'subscriptions' not in event:
            event['subscriptions'] = []
        if '_version' not in event:
            event['_version'] = 1
        subscriptions = event['subscriptions']
        users = {s['user'] for s in subscriptions}
        for subscription in scol.find({'event': event['_id']}).sort('date'):
            scount += 1
            if subscription['user'] in users:
                print(('WARNING: duplicate subscription for user:',
                       subscription['user']))
                continue
            users.add(subscription['user'])
            subscription2 = {
                'user': subscription['user']
            }
            if 'subscribedBy' in subscription:
                subscription2['inviter'] = subscription['subscribedBy']
                subscription2['inviterNotes'] = subscription[
                    'subscribedBy_notes']
                subscription2['inviteDate'] = subscription['date']
                if 'dateConfirmed' in subscription:
                    subscription2['history'] = [{
                        'state': 'subscribed',
                        'date': subscription['dateConfirmed'],
                    }]
            else:
                mutation = {
                    'state': 'subscribed',
                }
                if 'date' in subscription:
                    mutation['date'] = subscription['date']
                subscription2['history'] = [mutation]
            if 'userNotes' in subscription:
                subscription2['history'][0][
                    'notes'] = subscription['userNotes']
            subscriptions.append(subscription2)
        if 'mailBody' in event:
            event['subscribedMailBody'] = event['mailBody']
            del event['mailBody']
        if 'subscribedByOtherMailBody' in event:
            event['invitedMailBody'] = event['subscribedByOtherMailBody']
            del event['subscribedByOtherMailBody']
        ecol.update({'_id': event['_id']}, event)
        scol.remove({'event': event['_id']})
    print('Moved %d subscriptions into %d events.' % (scount, ecount))


if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
