#!/usr/bin/python

import datetime

import httplib2
from iso8601 import parse_date
from oauth2client.service_account import ServiceAccountCredentials

from django.conf import settings

try:
    # Debian package python-googleapi
    from apiclient.discovery import build
except ImportError:
    # pip package google-api-python-client
    from googleapiclient.discovery import build

# How to configure the agenda:
#
#  - Go to https://console.developers.google.com/project and make a new
#    project.
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
    return ServiceAccountCredentials.from_json_keyfile_name(
        settings.GOOGLE_OAUTH2_KEY,
        ['https://www.googleapis.com/auth/calendar.readonly'])


def parse_item_date(date):
    # dateTime: specific time
    if 'dateTime' in date:
        return parse_date(date['dateTime'])
    # date: all-day event
    return parse_date(date['date'] + 'T00:00:00Z')


def fetch_agenda(h, cal_id):
    timeMin = datetime.datetime.utcnow().date().isoformat() + 'T00:00:00Z'
    cal = build('calendar', 'v3', http=h, cache_discovery=False)
    request = cal.events().list(calendarId=cal_id,
                                timeMin=timeMin,
                                fields='items(summary,description,start,end)')
    response = request.execute()
    agenda = []
    for item in response['items']:
        agenda.append((item['summary'], item.get('description', ''),
                       parse_item_date(item['start']),
                       parse_item_date(item['end'])))
    return agenda


def fetch():
    h = httplib2.Http()
    credentials = get_credentials()
    credentials.authorize(h)

    try:
        agendas = {}
        for key, cal_id in settings.GOOGLE_CALENDAR_IDS.items():
            agendas[key] = fetch_agenda(h, cal_id)
        return agendas
    except httplib2.ServerNotFoundError:
        return None


if __name__ == '__main__':
    from kn.agenda.entities import update
    update(fetch())

# vim: et:sta:bs=2:sw=4:
