import logging

import MySQLdb
from tarjan.tc import tc

import kn.leden.entities as Es

from kn.leden.date import now

from django.conf import settings
from django.utils import six


def generate_wolk_changes(giedo):
    creds = settings.WOLK_MYSQL_SECRET
    if not creds:
        logging.warning('wolk: no credentials available, skipping')
        return None

    todo = {'addUser': [], 'addGroup': [],
            'addUserToGroup': [], 'removeUserFromGroup': []}
    dt_now = now()
    # First, lets see which users and groups to create
    users = dict()      # users to have
    groups = dict()     # groups to have
    missing_groups = set()
    missing_users = set()
    ulut = dict()
    for m in Es.by_name('leden').get_members():
        if not m.got_unix_user:
            continue
        ulut[m._id] = m
        users[str(m.name)] = m
    # Get all groups and create a look-up-table for group membership
    gs = tuple(Es.groups())
    mrels = Es.query_relations(how=None, _with=gs, _from=dt_now, until=dt_now)
    mlut = dict()
    for g in gs:
        mlut[g._id] = []
    for mrel in mrels:
        mlut[mrel['with']].append(mrel['who'])
    # Flatten out group membership.  For instance: if Giedo is in Kasco
    # and Kasco is in Boekenlezers, then Giedo is also in the Boekenlezers
    # unix group.
    # But first split the mlut graph into a group and a non-group subgraph.
    mlut_g = {}     # { <group> : <members that are groups> }
    mlut_ng = {}    # { <group> : <members that are not groups> }
    for g_id in mlut:
        mlut_g[g_id] = [c for c in mlut[g_id] if c in mlut]
        mlut_ng[g_id] = [c for c in mlut[g_id] if c not in mlut]
    mlut_g_tc = tc(mlut_g)  # transitive closure
    # Generate the { <group> : <indirect non-group members> } graph
    memb_graph = {}
    for g in gs:
        if not g.got_unix_group:
            continue
        memb_graph[g._id] = set(mlut_ng[g._id])
        for h_id in mlut_g_tc[g._id]:
            memb_graph[g._id].update(mlut_ng[h_id])
    # Fill the groups variable
    for g in gs:
        if not g.got_unix_group:
            continue
        groups[str(g.name)] = set([str(ulut[c].name)
                                   for c in memb_graph[g._id] if c in ulut])

    # Now, check which users and groups actually exist in owncloud
    missing_users = set(users.keys())
    missing_groups = set(groups.keys())
    dc = MySQLdb.connect(creds[0], user=creds[1],
                         passwd=creds[2], db=creds[3])
    c = dc.cursor()
    c.execute("SELECT gid, uid FROM oc_group_user")
    for group, user in c.fetchall():
        if group not in groups:
            continue
        if user not in users or user not in groups[group]:
            todo['removeUserFromGroup'].append((user, group))
            continue
        if user in groups[group]:
            groups[group].remove(user)
    c.execute("SELECT uid FROM oc_users")
    for user, in c.fetchall():
        if user not in users:
            logging.info("wolk: stray user %s", user)
            continue
        missing_users.remove(user)
    c.execute("SELECT gid FROM oc_groups")
    for group, in c.fetchall():
        if group not in groups:
            logging.info("wolk: stray group %s", user)
            continue
        missing_groups.remove(group)
    for user in missing_users:
        todo['addUser'].append((user, six.text_type(users[user].humanName)))
    todo['addGroup'] = list(missing_groups)
    for group, missing_members in six.iteritems(groups):
        for user in missing_members:
            todo['addUserToGroup'].append((user, group))
    return todo

# vim: et:sta:bs=2:sw=4:
