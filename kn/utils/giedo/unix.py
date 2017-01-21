from tarjan.tc import tc        # transitive closure of a graph

import kn.leden.entities as Es
from kn.base.conf import DT_MIN

from kn.leden.date import now


def generate_unix_map(giedo):
    ret = {'groups': {},
           'users': {}}
    dt_now = now()
    # Get all users
    ulut = dict()
    for u in Es.users():
        if not u.got_unix_user:
            continue
        ulut[u._id] = u
        ret['users'][str(u.name)] = {
                'full_name': u.full_name,
                'expire_date': DT_MIN.strftime('%Y-%m-%d')}
    member_relations_grouped = dict()
    for rel in Es.query_relations(_with=Es.by_name('leden'), until=dt_now):
        if rel['who'] not in member_relations_grouped:
            member_relations_grouped[rel['who']] = []
        member_relations_grouped[rel['who']].append(rel)
    for user_id, relations in member_relations_grouped.items():
        latest = max(relations, key=lambda x: x['until'])
        ret['users'][str(ulut[user_id].name)][ 'expire_date'] = (
                latest['until'].strftime('%Y-%m-%d'))

    # Get all groups and create a look-up-table for group membership
    gs = tuple(Es.groups())
    mrels = Es.query_relations(how=None, _with=gs, _from=dt_now,
                               until=dt_now)
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
    # Fill the return map
    for g in gs:
        if not g.got_unix_group:
            continue
        ret['groups'][str(g.name)] = [str(ulut[c].name)
                                      for c in memb_graph[g._id] if c in ulut]
    return ret

# vim: et:sta:bs=2:sw=4:
