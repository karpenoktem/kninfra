# vim: et:sta:bs=2:sw=4:
from __future__ import with_statement

import _import
import sys
from datetime import date, datetime
import kn.leden.entities as Es
from common import *

DAYS_IN_YEAR = 365.242199

def check_email():
    with open('check-email.template', 'r') as f:
        templ = f.read()

    for m in args_to_users(sys.argv[1:]):
        msgs = list()
        ## ___ oud ___    
        #if m.dateJoined is None:
        #    msgs.append("de datum van toetreden is onbekend")
        #else:
        #    if m.dateJoined < date(2004, 4, 1):
        #        msgs.append("je bent toegetreden voor "+
        #                "de constitutie")
        # 
        ## Het moment van toetreding wordt niet meer bijgehouden
        if m.dateOfBirth is None:
            msgs.append("je geboortedatum is onbekend")
        else:
            age = (datetime.now() - m.dateOfBirth).days \
                    / DAYS_IN_YEAR
            if age < 15:
                msgs.append("je bent jonger dan 15")
            elif age > 40:
                msgs.append("je bent ouder dan 40")
        addr = m.primary_address
        if addr == None:
            msgs.append("we missen jouw adres")
        else:
            if not addr['street']:
                msgs.append("we missen de straat van je adres")
            if not addr['zip']:
                msgs.append("we missen de postcode van je adres")
            if not addr['number']:
                msgs.append("we missen het huisnummer van je adres")
            if not addr['city']:
                msgs.append("van adres is geen plaats bekend")
        if not m.primary_telephone:
            msgs.append("jouw telefoonnummer is onbekend")
        if m.studentNumber is None:
            msgs.append("jouw studentnummer is onbekend")
        elif len(m.studentNumber) != 7:
            msgs.append("jouw studentnummer lijkt fout")
        if len(msgs) != 0:
            extra = 'Een paar zaken vallen op:\n'
            for i, msg in enumerate(msgs):
                if i == 0: msg = msg.capitalize()
                extra += ' - %s' % msg
                if i == len(msgs) - 2: extra += ' en\n'
                elif i == len(msgs) - 1: extra += '.\n'
                else: extra += ';\n'
        else:
            extra = ''
        study = m.proper_primary_study
        em = templ % (
            {'username': str(m), # returns the (user)name
             'firstName': m.first_name,
             'lastName': m.last_name,
             'fullName': m.full_name,
             'gender': ('onbekend' if m.gender is None
                else {'m': 'man',
                      'v': 'vrouw'}.get(m.gender, '?')),
             'dateOfBirth': ('onbekend' if m.dateOfBirth is None
                else str(m.dateOfBirth.date())),
             'dateJoined': 'onbekend',  # TODO:  Fix of remove
             'email': m.primary_email,
             'telephone': ('onbekend' if m.primary_telephone is None
                else m.primary_telephone),
             'addr_street': ('onbekend' if not addr
                else addr['street']),
             'addr_number': ('onbekend' if not addr
                else addr['number']),
             'addr_city': ('onbekend' if not addr 
                else addr['city']),
             'addr_zipCode': ('onbekend' if not addr
                else addr['zip']),
             'institute': ('onbekend' if (not study or not study['institute'])
                else study['institute'].humanName.humanName),
             'study': ('onbekend' if (not study or not study['study'])
                else study['study'].humanName.humanName), # ik verzin dit niet
             'studentNumber': ('onbekend' if not m.studentNumber
                else m.studentNumber),
             'extra': extra
            })
        print m.name
        m.email_user('Controle Karpe Noktem ledenadministratie',
             em, from_email='secretaris@karpenoktem.nl')

if __name__ == '__main__':
    check_email()
