import logging

import kn.leden.entities as Es
from kn.leden.date import now
from kn.settings import LISTS_MAILDOMAIN, MAILDOMAIN

# TODO (issue #7) handle cycles properly.

def generate_postfix_map(giedo):
    tbl = dict() # the virtual map
    non_mailman_groups = {}
    dt_now = now()
    id2email = {}
    # handle the straightforward cases
    for e in Es.all():
        if e.canonical_email is None:
            continue
        id2email[e._id] = e.canonical_email
        for nm in e.other_names:
            tbl["%s@%s" % (nm, MAILDOMAIN)] = (e.canonical_email,)
        if e.type == 'user':
            tbl[e.canonical_email] = (e.primary_email,)
        elif e.type == 'group':
            if e.got_mailman_list and e.name:
                tbl[e.canonical_email] = ('%s@%s' % (
                    str(e.name), LISTS_MAILDOMAIN),)
            else:
                tbl[e.canonical_email] = []
                non_mailman_groups[e._id] = e
        else:
            logging.warn("postfix: unhandled type: %s" % e.type)
        id_email = "%s@%s" % (e.id, MAILDOMAIN)
        if not id_email in tbl:
            tbl[id_email] = (e.canonical_email,)
    # handle the non-mailman groups
    for rel in Es.query_relations(_with=non_mailman_groups.keys(),
            _from=dt_now, until=dt_now, how=None):
        e = non_mailman_groups[rel['with']]
        email = id2email.get(rel['who'])
        if email is not None:
            tbl[e.canonical_email].append(email)
    return tbl

# vim: et:sta:bs=2:sw=4:
