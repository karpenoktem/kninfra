import logging

import protobufs.messages.daan_pb2 as daan_pb2

from django.conf import settings

import kn.leden.entities as Es
from kn.leden.date import now

# TODO (issue #7) handle cycles properly.


def generate_postfix_map():
    tbl = daan_pb2.PostfixMap()  # the virtual map
    non_mailman_groups = {}
    dt_now = now()
    id2email = {}
    # handle the straightforward cases
    for e in Es.all():
        if e.canonical_email is None:
            continue
        id2email[e._id] = e.canonical_email
        for nm in e.other_names:
            tbl.map["%s@%s" % (nm, settings.MAILDOMAIN)].values.append(e.canonical_email)
        if e.type == 'user':
            tbl.map[e.canonical_email].values.append(e.email)
        elif e.type == 'group':
            if e.got_mailman_list and e.name:
                tbl.map[e.canonical_email].values.append('%s@%s' % (
                    str(e.name), settings.LISTS_MAILDOMAIN))
            else:
                non_mailman_groups[e._id] = e
        else:
            logging.warn("postfix: unhandled type: %s" % e.type)
        id_email = "%s@%s" % (e.id, settings.MAILDOMAIN)
        if id_email not in tbl.map:
            tbl.map[id_email].values.append(e.canonical_email)
    # handle the non-mailman groups
    for rel in Es.query_relations(_with=list(non_mailman_groups),
                                  _from=dt_now, until=dt_now, how=None):
        e = non_mailman_groups[rel['with']]
        email = id2email.get(rel['who'])
        if email is not None:
            tbl.map[e.canonical_email].values.append(email)
    return tbl


def generate_postfix_slm_map():
    # We generate the postfix "sender_login_maps".
    # This is used to decide by postfix whether a given user is allowed to
    # send e-mail as if it was coming from a particular e-mail address.
    # We only allow members to send e-mail
    ret = daan_pb2.PostfixMap()
    for member in Es.by_name('leden').get_members():
        for email in member.email_from_addresses:
            ret.map[email].values.append(str(member.name))
    return ret

# vim: et:sta:bs=2:sw=4:
