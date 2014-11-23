#!/usr/bin/python

from iso8601 import parse_date
import kn.settings as settings
import json
import datetime

# pip install google-api-python-client
from oauth2client.client import SignedJwtAssertionCredentials
from googleapiclient.discovery import build
import httplib2

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

# See https://developers.google.com/api-client-library/python/apis/calendar/v3
# for documentation about the APIs used here.

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

    cal = build('calendar', 'v3', http=h)
    request = cal.events().list(calendarId=settings.GOOGLE_CALENDAR_ID, timeMin=timeMin, fields='items(summary,description,start,end)')
    response = request.execute()

    agenda = []
    for item in response['items']:
        agenda.append((item['summary'], item['description'],
                       parse_item_date(item['start']),
                       parse_item_date(item['end'])))

    return agenda


if __name__ == '__main__':
    from kn.agenda.entities import update
    update(fetch())

# vim: et:sta:bs=2:sw=4:
