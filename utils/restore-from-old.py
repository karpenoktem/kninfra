# vim: et:sta:bs=2:sw=4:
import _import # noqa: F401

from datetime import datetime, timedelta
from time import strptime
import logging
import json
import sys

from tarjan import tarjan

import kn.leden.entities as Es
import kn.subscriptions.entities as subscr_Es
import kn.moderation.entities as mod_Es
from kn.base.conf import from_settings_import
from_settings_import("DT_MIN", "DT_MAX", globals())
from kn.utils.giedo.db import update_db


def main(data):
    def str_to_date(s):
        if s is None:
            return None
        return datetime(*strptime(s, '%Y-%m-%d')[:3])

    def year_to_dates(year):
        return (datetime(2003+year, 9, 1),
            datetime(2004+year, 8, 31))

    def create_tag(name, humanName, tags=[]):
        return Es.ecol.insert({'types': ['tag'],
                       'names': [name],
                       'humanNames': [{
                           'name': name,
                           'human': humanName}],
                       'tags': tags})
    print 'dropping'
    Es.ecol.drop()
    Es.rcol.drop()
    Es.mcol.drop()
    subscr_Es.ecol.drop()
    subscr_Es.scol.drop()
    print 'creating indices'
    Es.ensure_indices()
    subscr_Es.ensure_indices()
    mod_Es.ensure_indices()
    conv_inst = dict()
    conv_study = dict()
    conv_group = dict()
    conv_group_byname = dict()
    conv_event = dict()
    conv_seat = dict()
    conv_user = dict()
    ignore_groups = frozenset(['leden-oud'])
    ignore_groups_members = frozenset(['leden'])
    ignore_groups_ids = set()
    ignore_groups_members_ids = set()
    year_groups = frozenset(
        ['leden'+str(x) for x in range(1, 9)] +
        ['kasco'+str(x) for x in range(1, 9)] +
        ['bestuur'+str(x) for x in range(1, 9)])
    year_groups_ids = dict()
    year_groups_lut = {}
    print 'initial tags'
    system_tag = create_tag('!system', 'Systeemstempels')
    year_overrides_tag = create_tag('!year-overrides',
            'Jaarlidmaatschapstempels', [system_tag])
    virtual_group_tag = create_tag("!virtual-group",
            'Virtuele groep', [system_tag])
    sofa_brand_tag = create_tag("!sofa-brand",
            'Sofa merk', [system_tag])
    year_group_tag = create_tag("!year-group", 'Jaargroep',
            [system_tag])
    for i in xrange(1, 9):
        Es.ecol.insert({'types': ['tag'],
                'humanNames': [{'human': 'Wel jaar %s' % i}],
                'year-override': {'year': i,
                          'type': True},
                'tags': [year_overrides_tag]})
        Es.ecol.insert({'types': ['tag'],
                'humanNames': [{'human': 'Niet jaar %s' % i}],
                'year-override': {'year': i,
                          'type': False},
                'tags': [year_overrides_tag]})
    print 'institutes'
    for m in data['EduInstitute']:
        n = {   'types': ['institute'],
            'humanNames': [{'human': m['name']}]}
        conv_inst[m['id']] = Es.ecol.insert(n)
    print 'studies'
    for m in data['Study']:
        n = {   'types': ['study'],
            'humanNames': [{'human': m['name']}]}
        conv_study[m['id']] = Es.ecol.insert(n)
    print 'initial groups'
    conv_group_byname['bestuur'] = {
        'id': Es.ecol.insert({
            'types': ['group'],
            'names': ['bestuur'],
            'tags': [year_group_tag],
            'humanNames': [{
                'name': 'bestuur',
                'human': 'Bestuur',
                'genitive_prefix': 'van het'}],
            'description': "Het bestuur"}),
        'name': 'bestuur',
        'humanName': 'Bestuur'}
    conv_group_byname['kasco'] = {
        'id': Es.ecol.insert({
            'types': ['group'],
            'names': ['kasco'],
            'tags': [year_group_tag],
            'humanNames': [{
                'name': 'kasco',
                'human': 'Kascontrolecommissie',
                'genitive_prefix': 'van de'}],
            'description': "De kascontrolecommissie"}),
        'name': 'kasco',
        'humanName': 'Bestuur'}
    print 'groups'
    for m in data['OldKnGroup']:
        if m['name'] in ignore_groups:
            ignore_groups_ids.add(m['id'])
            continue
        if m['name'] in ignore_groups_members:
            ignore_groups_members_ids.add(m['id'])
        if m['name'] in year_groups:
            year_groups_ids[m['id']] = m['name']
            group = m['name'][:-1]
            year = int(m['name'][-1:])
            year_groups_lut[m['id']] = (group, year)
            continue
        if m['name'] == 'leden':
            m['isVirtual'] = False # fix for leden
        n = {   'types': ['tag' if m['isVirtual'] else 'group'],
            'names': [m['name']],
            'humanNames': [{
                'name': m['name'],
                'human': m['humanName'],
                'genitive_prefix': m['genitive_prefix']
                }],
            'description': m['description'],
            'temp': {
                'is_virtual': m['isVirtual']
            }
            }
        conv_group[m['id']] = {'id': Es.ecol.insert(n),
                       'name': m['name'],
                       'humanName': m['humanName']}
        conv_group_byname[m['name']] = conv_group[m['id']]
    print 'group hierarchy'
    for m in data['OldKnGroup']:
        if m['name'] in year_groups or m['name'] in ignore_groups:
            continue
        if m['parent'] is not None:
            if not m['parent'] in conv_group:
                print " %s was orphaned" % m['name']
                continue
            Es.ecol.update({'_id': conv_group[m['id']]['id']},
                {'$push': {'tags': conv_group[
                            m['parent']]['id']}})
    print 'users'
    for m in data['OldKnUser']:
        bits = m['password'].split('$')
        if len(bits) == 3:
            pwd = {'algorithm': bits[0],
                   'salt': bits[1],
                   'hash': bits[2]}
        else:
            pwd = None
        n = {
            'types': ['user'],
            'names': [m['username']],
            'humanNames': [{'human': m['first_name'] + ' ' +
                         m['last_name']}],
            'person': {
                'titles': [],
                'nick': m['first_name'],
                'given': None,
                'family': m['last_name'],
                'gender': m['gender'],
                'dateOfBirth': str_to_date(m['dateOfBirth'])
            },
            'emailAddresses': [
                {'email': m['email'],
                 'from': DT_MIN,
                 'until': DT_MAX
                }],
            'addresses': [
                {'street': m['addr_street'],
                 'number': m['addr_number'],
                 'zip': m['addr_zipCode'],
                 'city': m['addr_city'],
                 'from': DT_MIN,
                 'until': DT_MAX
                }],
            'telephones': [
                {'number': m['telephone'],
                 'from': DT_MIN,
                 'until': DT_MAX}],
            'studies': [
                {'institute': conv_inst.get(m['institute']),
                 'study': conv_study.get(m['study']),
                 'from': DT_MIN,
                 'until': DT_MAX,
                 'number': m['studentNumber']}
            ],
            'temp': {
                'oud': m['in_oud'],
                'aan': m['in_aan'],
                'incasso': m['got_incasso'],
                'joined': m['dateJoined'],
                'remarks': m['remarks']
            },
            'is_active': m['is_active'],
            'password': pwd
            }
        conv_user[m['id']] = Es.ecol.insert(n)
        for g in m['groups']:
            if g in ignore_groups_ids or \
                    g in ignore_groups_members_ids:
                continue
            if g in year_groups_ids:
                gname, year = year_groups_lut[g]
                f, u = year_to_dates(year)
                Es.rcol.insert({
                    'with': conv_group_byname[gname]['id'],
                    'who': conv_user[m['id']],
                    'from': f,
                    'until': u,
                    'how': None})
                continue
            Es.rcol.insert({
                'with': conv_group[g]['id'],
                'who': conv_user[m['id']],
                'from': DT_MIN,
                'until': DT_MAX,
                'how': None})
    print 'brands'
    for m in data['OldSeat']:
        if m['name'] == 'deelhoofd':
            m['name'] = 'graficideelhoofd'
        if m['name'] in conv_seat:
            continue
        n = {'types': ['brand'],
             'names': [m['name']],
             'tags': [sofa_brand_tag],
             'humanNames': [{'name': m['name'],
                     'human': m['humanName']}]}
        conv_seat[m['name']] = {'id': Es.ecol.insert(n)}
    print 'seats'
    for m in data['OldSeat']:
        if m['group'] in year_groups_ids:
            gname = year_groups_ids[m['group']]
            gdat = conv_group_byname[gname[:-1]]
            _from, until = year_to_dates(int(gname[-1:]))
        else:
            gdat = conv_group[m['group']]
            _from, until = DT_MIN, DT_MAX
        n = {'types': ['group'],
             'names': [gdat['name'] + '-' + m['name']],
             'description': [m['description']],
             'tags': [virtual_group_tag],
             'virtual': {
                 'type': 'sofa',
                 'with': gdat['id'],
                 'how': conv_seat[m['name']]['id']},
             'humanNames': [{
                    'name': gdat['name'] + '-' + m['name'],
                'human': m['humanName'] +
                    ' ' + gdat['humanName']}]}
        i = Es.ecol.insert(n)
        Es.rcol.insert({'who': conv_user[m['user']],
                'from': _from,
                'until': until,
                'how': conv_seat[m['name']]['id'],
                'with': gdat['id']})
    print 'merging relations'
    print ' list until'
    lut = dict()
    plan_changes = dict()
    plan_remove = set()
    for r in Es.rcol.find({'until': {'$lt': DT_MAX}}):
        lut[r['until'] + timedelta(1, 0), r['with'],
                r['how'], r['who']] = r['_id']
    print ' crossreference from'
    for r in Es.rcol.find({'from': {'$gt': DT_MIN}}):
        n = (r['from'], r['with'], r['how'], r['who'])
        if n not in lut:
            continue
        plan_changes[lut[n]] = (r['until'], r['_id'])
        plan_remove.add(r['_id'])
    print ' transitive closure of plan'
    print 'small final tweaks to groups'
    Es.ecol.update({'names': 'leden'}, {'$push': {'tags': year_group_tag}})
    done = False
    while not done:
        done = True
        for k, v in plan_changes.iteritems():
            if v[1] in plan_changes:
                plan_changes[k] = plan_changes[v[1]]
                del plan_changes[v[1]]
                done = False
                break
    print ' execute'
    for r in plan_remove:
        Es.rcol.remove({'_id': r})
    for k, v in plan_changes.iteritems():
        Es.rcol.update({'_id': k}, {'$set': {'until': v[0]}})
    print 'event'
    for m in data['Event']:
        if m['owner'] not in conv_group:
            gname = year_groups_lut[m['owner']][0]
            gid = conv_group_byname[gname]['id']
        else:
            gid = conv_group[m['owner']]['id']
        conv_event[m['id']] = subscr_Es.ecol.insert({
            'mailBody': m['mailBody'],
            'humanName': m['humanName'],
            'description': m['description'],
            'cost': m['cost'],
            'is_open': m['is_open'],
            'owner': gid,
            'name': m['name']})
    print 'event subscriptions'
    for m in data['EventSubscription']:
        subscr_Es.scol.insert({
            'event': conv_event[m['event']],
            'userNotes': m['userNotes'],
            'debit': m['debit'],
            'user': conv_user[m['user']]})
    print 'giedo updatedb'
    update_db(None)
    print 'alias'
    print ' ids_by_names'
    name2id = Es.ids_by_names()
    print ' to graph'
    alias_graph = {}
    for m in data['Alias']:
        alias_graph[m['source']] = m['target']
    print ' tarjan'
    for scc in tarjan(alias_graph):
        assert len(scc) == 1
        src = scc[0]
        if src in name2id:
            continue
        if src not in alias_graph:
            continue
        if not alias_graph[src] in name2id:
            print '  ? %s -> %s' % (src, alias_graph[src])
            continue
        name2id[src] = name2id[alias_graph[src]]
        Es.ecol.update({'names': alias_graph[src]},
                   {'$push': {'names': src}})

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    if len(sys.argv) == 1:
        sys.argv.append('old.json')
    print 'loading json'
    d = {}
    for fn in sys.argv[1:]:
        print ' %s'%fn
        with open(fn) as f:
            d_bit = json.load(f)
            for k, v in d_bit.iteritems():
                if k not in d:
                    d[k] = []
                d[k].extend(v)
    main(d)
