#!/usr/bin/python

from oauth2client.client import SignedJwtAssertionCredentials
import httplib2
from iso8601 import parse_date
import kn.settings as settings
import json
import datetime

# How to configure the agenda:
#
#  - Go to https://console.developers.google.com/project and make a new project.
#  - Under APIs & auth / APIs, enable the Calendar API (you can disable all
#    other APIs).
#  - Under APIs & auth / Credentials, create a new Client ID, with type
#    Service account.
#  - Download a key using 'Generate new JSON key' and remove the p12 key file
#    and fingerprint.
#  - Store the JSON file in a safe location (it should not be public) and
#    update settings.py to point to it (GOOGLE_OAUTH2_KEY is the path to the
#    JSON file).
#
# Note that this script itself should be run with the repository (for example
# /home/infra/repo) in PYTHONPATH.

def get_credentials():
    key = json.loads(open(settings.GOOGLE_OAUTH2_KEY, 'r').read())
    return SignedJwtAssertionCredentials(service_account_name=key['client_email'],
                                         private_key=key['private_key'],
                                         scope='https://www.googleapis.com/auth/calendar.readonly',
                                         user_agent='Karpe Noktem agenda fetcher')

def parse_item_date(date):
    # dateTime: specific time
    if 'dateTime' in date:
        return parse_date(date['dateTime'])
    # date: all-day event
    return parse_date(date['date']+'T00:00:00Z')


def fetch():
    h = httplib2.Http()
    credentials = get_credentials()
    credentials.authorize(h)

    timeMin = datetime.datetime.utcnow().date().isoformat() + 'T00:00:00Z'
    resp, content = h.request('https://www.googleapis.com/calendar/v3/calendars/{id}/events?orderBy=startTime&showDeleted=false&singleEvents=true&timeMin={timeMin}&fields=items(description%2Cend%2Cstart%2Csummary)'.format(id=settings.GOOGLE_CALENDAR_ID, timeMin=timeMin))

    if not resp['content-type'].startswith('application/json'):
        print 'Wrong content type'
        exit(1)

    data = json.loads(content)

    if resp.status != 200:
        print 'HTTP error %d: %s' % (data['error']['code'],
                                     data['error']['message'])
        exit(1)

    agenda = []
    for item in data['items']:
        agenda.append((item['summary'], item['description'],
                       parse_item_date(item['start']),
                       parse_item_date(item['end'])))

    return agenda


if __name__ == '__main__':
    from kn.agenda.entities import update
    update(fetch())

# vim: et:sta:bs=2:sw=4:
