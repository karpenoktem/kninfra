# vim: et:sta:bs=2:sw=4:
import _import
from common import *

from kn.leden.models import OldKnUser, OldKnGroup
from datetime import date, datetime
import sys
import re

def check_members(members):
    ledeng = dict()
    c = 0
    while True:
        c += 1
        ms = date(2004 + c, 8, 1)
        if datetime.now().date() < ms:
            break
        ledeng[c] = OldKnGroup.objects.get(name='leden%s' % c)

    for m in members:
        if m.dateJoined is None:
            print "%s: dateJoined is None" % m.username
        else:
            if m.dateJoined < date(2004, 4, 1):
                print "%s: joined before constitution" % \
                        m.username
            c = 0
            while True:
                c += 1
                ms = date(2004 + c, 8, 1)
                if datetime.now().date() < ms:
                    break
                if m.dateJoined > ms:
                    continue
                if len(ledeng[c].user_set.filter(
                        username=m.username)) == 0:
                    print "%s: should be in leden%s" \
                            % (m.username, c)

        if m.dateOfBirth is None:
            print "%s: dateOfBirth is None" % m.username
        else:
            age = (datetime.now().date() - m.dateOfBirth).days \
                    / DAYS_IN_YEAR
            if age < 15:
                print "%s: age < 15" % m.username
            elif age > 40:
                print "%s: age > 40" % m.username
        if m.password == '$$' or \
           m.password == '':
            print "%s: no empty password" % m.username
        if m.addr_street == '':
            print "%s: no empty addr_street" % m.username
        if m.addr_zipCode == '':
            print "%s: no empty addr_zipCode" % m.username
        elif not re.match("^[0-9]{4} [A-Z]{2}$", m.addr_zipCode):
            print "%s: strange addr_zipCode" % m.username
        if m.addr_number == '':
            print "%s: no empty addr_number" % m.username
        if m.addr_city == '':
            print "%s: no empty addr_city" % m.username
        if m.telephone is None:
            print "%s: telephone is None" % m.username
        elif m.telephone == '':
            print "%s: empty telephone" % m.username
        elif not m.telephone[0:1] == '+':
            print "%s: un-normalised telephone" % m.username
        if m.institute_id in [INST_RU, INST_HAN] and \
                m.studentNumber is None:
            print "%s: studentNumber is None" % m.username
        else:
            if (m.institute_id == INST_RU and len(m.studentNumber) != 7) or \
               (m.institute_id == INST_HAN and len(m.studentNumber) != 6):
                print "%s: student number of incorrect length" \
                    % m.username

        if (not m.is_active and
                len(m.groups.filter(name=MEMBER_GROUP)) > 0):
            print "%s: not active" % m.username

if __name__ == '__main__':
    check_members(args_to_users(sys.argv[1:]))
