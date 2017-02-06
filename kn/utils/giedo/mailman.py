import logging

from django.utils import six

import kn.leden.entities as Es
from kn.leden.date import now


def generate_mailman_changes(giedo):
    todo = {'create': [], 'add': {}, 'remove': {}}
    # TODO mm_groups and mm_rels
    # Get the groups that need a mailing list and the members of those
    # groups.
    dt_now = now()
    mm_groups = [g for g in Es.groups() if g.got_mailman_list and g.name]
    mm_rels = Es.query_relations(_with=mm_groups, how=None, _from=dt_now,
                                 until=dt_now, deref_who=True)
    # Get the current mailing list membersip
    ml_membership = giedo.hans.send({'type': 'maillist-get-membership'})

    # membership_to_check will contain the current membership of the
    # mailinglists for which there are groups.  We will remove users
    # from membership_to_check if we see these users are in the groups.
    # In the end membership_to_check contains the stray users.
    membership_to_check = {}
    gid2name = dict()
    # Find the current members of the mailing lists and find which
    # mailing lists are missing.
    for g in mm_groups:
        name = str(g.name).encode()
        gid2name[g._id] = name
        if name in ml_membership:
            membership_to_check[name] = set(ml_membership[name])
        else:
            todo['create'].append((name, six.text_type(g.humanName)))
            membership_to_check[name] = set()

    # Check which memberships are missing in the current mailing lists
    for rel in mm_rels:
        em = rel['who'].canonical_email.encode()
        gname = gid2name[rel['with']]
        if em not in membership_to_check[gname]:
            if gname not in todo['add']:
                todo['add'][gname] = []
            todo['add'][gname].append(em)
        else:
            membership_to_check[gname].remove(em)

    # Check which memberships are superfluous in the current mailing lists
    for n in ml_membership:
        if n not in membership_to_check:
            logging.warning("Unaccounted e-maillist %s" % n)
            continue
        for em in membership_to_check[n]:
            if n not in todo['remove']:
                todo['remove'][n] = []
            todo['remove'][n].append(em)
    return todo

# vim: et:sta:bs=2:sw=4:
