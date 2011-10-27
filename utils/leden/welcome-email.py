# vim: et:sta:bs=2:sw=4:
from __future__ import with_statement

import _import
import sys
from django.core.mail import EmailMessage
from kn.leden.models import OldKnUser
from common import *

def welcome_email():
    with open('welcome-email.template', 'r') as f:
        templ = f.read()

    for m in args_to_users(sys.argv[1:]):
        em = templ % (
            {'username': m.username,
             'firstName': m.first_name,
             'lastName': m.last_name,
             'fullName': m.full_name(),
             'gender': ('onbekend' if m.gender is None
                else {'m': 'man',
                      'v': 'vrouw'}.get(m.gender, '?')),
             'dateOfBirth': ('onbekend' if m.dateOfBirth is None
                else str(m.dateOfBirth)),
             'dateJoined': ('onbekend' if m.dateJoined is None
                else str(m.dateJoined)),
             'email': m.email,
             'telephone': ('onbekend' if m.telephone is None
                else m.telephone),
             'addr_street': ('onbekend' if m.telephone is None
                else m.addr_street),
             'addr_number': ('onbekend' if m.telephone is None
                else m.addr_number),
             'addr_city': ('onbekend' if m.telephone is None
                else m.addr_city),
             'addr_zipCode': ('onbekend' if m.telephone is None
                else m.addr_zipCode),
             'institute': ('onbekend' if m.telephone is None
                else m.institute),
             'study': ('onbekend' if m.telephone is None
                else m.study),
             'studentNumber': ('onbekend' if m.telephone is None
                else m.studentNumber),
            })
        email = EmailMessage( "Welkom bij Karpe Noktem!", em,
            'Secretaris Karpe Noktem <secretaris@karpenoktem.nl>',
            [m.email], ['bestuur@karpenoktem.nl'])
        email.send()

if __name__ == '__main__':
    welcome_email()