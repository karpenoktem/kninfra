from __future__ import absolute_import

import logging

import kn.leden.entities as Es
from kn.leden.date import now
from kn.utils.mailman import import_mailman

import_mailman()

import Mailman           # noqa: E402 isort:skip
import Mailman.Utils     # noqa: E402 isort:skip
import Mailman.MailList  # noqa: E402 isort:skip


def generate_mailman_changes(giedo):
    todo = {'create': [], 'add': {}, 'remove': {}}
    # TODO mm_groups and mm_rels
    # Get the groups that need a mailing list and the members of those
    # groups.
    dt_now = now()
    mm_groups = [g for g in Es.groups() if g.got_mailman_list and g.name]
    mm_rels = Es.query_relations(_with=mm_groups, how=None, _from=dt_now,
                                 until=dt_now, deref_who=True)
    # TODO do we want to cache these?
    # Get the current mailing lists
    ml_names = frozenset(Mailman.Utils.list_names())
    ml_members = dict()
    gid2name = dict()
    # Find the current members of the mailing lists and find which
    # mailing lists are missing.
    for g in mm_groups:
        gid2name[g._id] = str(g.name)
        if not str(g.name) in ml_names:
            todo['create'].append((str(g.name),
                                   unicode(g.humanName)))
            c_ms = set([])
        else:
            c_ms = set([x[0] for x in
                        Mailman.MailList.MailList(
                            str(g.name),
                            lock=False
            ).members.iteritems()])
        ml_members[str(g.name)] = c_ms
    # Check which memberships are missing in the current mailing lists
    for rel in mm_rels:
        em = rel['who'].canonical_email
        gname = gid2name[rel['with']]
        if em not in ml_members[gname]:
            if gname not in todo['add']:
                todo['add'][gname] = []
            todo['add'][gname].append(em)
        else:
            ml_members[gname].remove(em)
    # Check which memberships are superfluous in the current mailing lists
    for n in ml_names:
        if n not in ml_members:
            logging.warning("Unaccounted e-maillist %s" % n)
            continue
        for em in ml_members[n]:
            if n not in todo['remove']:
                todo['remove'][n] = []
            todo['remove'][n].append(em)
    return todo

# vim: et:sta:bs=2:sw=4:
