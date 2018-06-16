# vim: et:sta:bs=2:sw=4:

import _import  # noqa: F401
import sys

from common import args_to_users

import kn.leden.entities as Es
from kn.base.mail import render_then_email
from kn.leden.mongo import _id


def check_email():
    comm_ids = [_id(x) for x in Es.by_name('comms').get_bearers()]
    list_ids = [_id(x) for x in Es.by_name('lists-opted').get_bearers()]
    for m in args_to_users(sys.argv[1:]):
        rels = m.get_related()
        rels = sorted(rels, key=lambda x: Es.entity_humanName(x['with']))
        comms = []
        lists = []
        others = []
        for rel in rels:
            if Es.relation_is_virtual(rel):
                continue
            if _id(rel['with']) in comm_ids:
                comms.append(rel)
            elif _id(rel['with']) in list_ids:
                lists.append(rel)
            else:
                others.append(rel)
        print(m.name)
        render_then_email('leden/check-email.mail.html',
                          m.email,
                          {'u': m,
                           'comms': comms,
                           'lists': lists,
                           'others': others},
                          from_email='secretaris@karpenoktem.nl')


if __name__ == '__main__':
    check_email()
