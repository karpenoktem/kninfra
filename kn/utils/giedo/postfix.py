import logging

import protobufs.messages.daan_pb2 as daan_pb2
from tarjan.tc import tc

from django.conf import settings
from django.utils import six

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
    # It is a dictionary { <email address> : [ <allowed user>, ... ] }
    tbl = dict()
    dt_now = now()
    # Get all users
    ulut = dict()
    # We only allow members to send e-mail
    for u in Es.by_name('leden').get_members():
        ulut[u._id] = u
        for name in u.names:
            if str(name) not in tbl:
                tbl[str(name)] = set()
            tbl[str(name)].add(str(u.name))
    # There are two kind of groups: groups whose members are allowed to
    # send e-mail as if coming from the group itself and those where this
    # is not allowed.  For convenience, lets call the first kind the
    # impersonatable groups.
    # Get all impersonatable groups and create a look-up-table for
    # group membership
    gs = list()
    for g in Es.groups():
        # TODO add a tag to force a group either impersonatable or not
        if not g.got_mailman_list:
            gs.append(g)
    mrels = Es.query_relations(how=None, _with=gs, _from=dt_now, until=dt_now)
    mlut = dict()
    for g in gs:
        mlut[g._id] = []
    for mrel in mrels:
        mlut[mrel['with']].append(mrel['who'])
    # Flatten out group membership.  For instance: if Giedo is in Kasco
    # and Kasco is in Boekenlezers, then Giedo is also in the Boekenlezers
    # unix group.
    # But first split the mlut graph into a impersonatable group
    # and a non-group subgraph.
    mlut_g = {}     # { <group> : <members that are impersonatable groups> }
    mlut_u = {}    # { <group> : <members that are users> }
    for g_id in mlut:
        mlut_g[g_id] = [c for c in mlut[g_id] if c in mlut]
        mlut_u[g_id] = [c for c in mlut[g_id] if c in ulut]
    mlut_g_tc = tc(mlut_g)  # transitive closure
    for g in gs:
        to_consider = tuple(mlut_g_tc[g._id]) + (g._id,)
        for sg_id in to_consider:
            for u_id in mlut_u[sg_id]:
                for name in g.names:
                    if str(name) not in tbl:
                        tbl[str(name)] = set()
                    tbl[str(name)].add(str(ulut[u_id].name))
    # Clean up tbl to return.
    ret = daan_pb2.PostfixMap()
    for name, users in six.iteritems(tbl):
        if not users:
            continue
        ret.map["%s@%s" % (name, settings.MAILDOMAIN)].values.extend(users)
    return ret

# vim: et:sta:bs=2:sw=4:
