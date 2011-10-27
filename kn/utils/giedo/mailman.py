# vim: et:sta:bs=2:sw=4:
import kn.leden.entities as Es
import logging

from kn.utils.mailman import import_mailman
from kn.leden.date import now
import_mailman()
import Mailman
import Mailman.Utils
import Mailman.MailList

def generate_mailman_changes(giedo):
    todo = {'create': [], 'add': {}, 'remove': {}}
    # TODO mm_groups and mm_rels
    # Get the groups that need a mailing list and the members of those
    # groups.
    dt_now = now()
    mm_groups = [g for g in Es.groups() if g.got_mailman_list]
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
                Mailman.MailList.MailList(str(g.name),
                    lock=False).members.iteritems()])
        ml_members[str(g.name)] = c_ms
    # Check which memberships are missing in the current mailing lists
    for rel in mm_rels:
        em = rel['who'].canonical_email
        gname = gid2name[rel['with']]
        if not em in ml_members[gname]:
            if not gname in todo['add']:
                todo['add'][gname] = []
            todo['add'][gname].append(em)
        else:
            ml_members[gname].remove(em)
    # Check which memberships are superfluous in the current mailing lists
    for n in ml_names:
        if not n in ml_members:
            logging.warning("Unaccounted e-maillist %s" % n)
            continue
        for em in ml_members[n]:
            if not n in todo['remove']:
                todo['remove'][n] = []
            todo['remove'][n].append(em)
    return todo