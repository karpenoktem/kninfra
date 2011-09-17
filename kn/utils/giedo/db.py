import logging
import kn.leden.entities as Es
from kn.leden.date import now
from kn.settings import DT_MIN, DT_MAX

def update_db(giedo):
        dt_now = now()
        # Load tags
        # TODO cache this
        tags = Es.ids_by_names(('!year-group', '!year-overrides',
                        '!virtual-group', '!sofa-brand'))
        year_overrides = {}
        for t in Es.bearers_by_tag_id(tags['!year-overrides'], _as=Es.Tag):
                year_overrides[t._id] = (t._data['year-override']['type'],
                                          t._data['year-override']['year'])

        # Load _id -> name lut.
        id2name = Es.names_by_ids()
        # Load groups and brands
        groups = Es.of_type_by_name('group')
        groups_set = frozenset(groups.values())
        # Find groups that have a virtual group for each year
        year_groups = [g for g in groups.itervalues()
                        if tags['!year-group'] in g.tag_ids]
        # Find relations on those groups and add the years for which those
        # relations hold.
        def add_years_to_relations(rels):
                until_years = [Es.date_to_year(r['until']) for r in rels
                                        if r['until'] != DT_MAX]
                max_until = max(max(until_years) if until_years else 0,
                                Es.date_to_year(dt_now))
                from_years = [Es.date_to_year(r['from']) for r in rels
                                        if r['from'] != DT_MIN]
                min_from = min(min(from_years) if from_years else
                                Es.date_to_year(dt_now),
                                Es.date_to_year(dt_now))
                for rel in rels:
                        s = min_from if rel['from'] == DT_MIN \
                                        else Es.date_to_year(rel['from'])
                        t = max_until if rel['until'] == DT_MAX \
                                        else Es.date_to_year(rel['until'])
                        years = set(range(s, t+1))
                        for tid in rel.get('tags', ()):
                                if tid not in year_overrides:
                                        continue
                                yr, tp = year_overrides[tid]
                                if tp:
                                        years.add(yr)
                                else:
                                        years.remove(yr)
                        rel['years'] = years
        year_group_mrels = tuple(Es.query_relations(
                _with=year_groups))
        # Check whether all year groups are created
        for g in year_groups:
                mrels = filter(lambda x: x['with']==g._id, year_group_mrels)
                add_years_to_relations(mrels)
                years = set()
                for rel in mrels:
                        years.update(rel['years'])
                for year in years:
                        n = str(g.name) + str(year)
                        if n not in groups:
                                logging.info("Creating yeargroup %s" % n)
                                _create_yeargroup(g, year, n, tags, groups,
                                               id2name)
        # Find all virtual groups
        virtual_groups = [g for g in groups_set
                        if tags['!virtual-group'] in g.tag_ids]
        sofa_vgroups = []
        yeargroup_vgroups = []
        for vg in virtual_groups:
                if vg._data['virtual']['type'] == 'sofa':
                        sofa_vgroups.append(vg)
                elif vg._data['virtual']['type'] == 'year-group':
                        yeargroup_vgroups.append(vg)
                else:
                        logging.warn("Unknown vgroup type: %s" \
                                        % vg._data['virtua']['type'])
        # Find all relations with the sofa virtual groups
        def relkey(rel):
                return (rel['who'], rel['how'], rel['with'],
                                rel['from'], rel['until'])
        vgroup_rlut = dict()
        for rel in Es.query_relations(_with=virtual_groups):
                vgroup_rlut[relkey(rel)] = rel['_id']
        # create look up table of existing sofas
        sofa_queries = []
        sofa_lut = dict()
        for svg in sofa_vgroups:
                w = dict(svg._data['virtual'])
                sofa_queries.append({'how': w['how'],
                                     'with': w['with']})
                k = (w['how'], w['with'])
                if k not in sofa_lut:
                        sofa_lut[k] = []
                sofa_lut[k].append(svg)
        # Check whether all year-group relations are in place
        for mrel in year_group_mrels:
                g = groups[id2name[mrel['with']]]
                for year in mrel['years']:
                        yg = groups[str(g.name) + str(year)]
                        rrel = {'who': mrel['who'],
                                'with': yg._id,
                                'how': mrel['how'],
                                'from': DT_MIN,
                                'until': DT_MAX}
                        if not relkey(rrel) in vgroup_rlut:
                                logging.info("vgroup: adding %s -> %s (%s)" % (
                                                id2name[mrel['who']], yg.name,
                                                id2name.get(mrel['how'])))
                                Es.rcol.insert(rrel)
                        else:
                                del vgroup_rlut[relkey(rrel)]
        # Check whether all sofas are created
        sofa_brands = {}
        for b in Es.brands():
                if tags['!sofa-brand'] not in b._data['tags']:
                        continue
                sofa_brands[b._id] = b
        for rel in Es.query_relations(how=sofa_brands.values()):
                if (rel['how'], rel['with']) in sofa_lut:
                        continue
                g = groups[id2name[rel['with']]]
                nm = str(g.name) + '-' + sofa_brands[rel['how']].sofa_suffix
                logging.info("creating sofa %s" % nm)
                n = {'types': ['group','tag'],
                     'names': [nm],
                     'tags': [tags['!virtual-group']],
                     'virtual': {
                             'type': 'sofa',
                             'with': rel['with'],
                             'how': rel['how']},
                     'humanNames': [{
                             'name': nm,
                             'human': unicode(g.humanName) + ' ' +
                                unicode(sofa_brands[rel['how']].humanName)}]}
                n['_id'] = Es.ecol.insert(n)
                groups[nm] = Es.Group(n)
                id2name[n['_id']] = nm
                sofa_vgroups.append(g)
                sofa_lut[rel['how'], rel['with']] = [groups[nm]]
                sofa_queries.append({'how': rel['how'],
                                     'with': rel['with']})
        # Find all relations for the sofa virtual groups and check whether
        # the appropriate relations to the sofas are generated
        for rel in Es.disj_query_relations(sofa_queries):
                for svg in sofa_lut[(rel['how'], rel['with'])]:
                        rrel = {'how': None,
                                'from': rel['from'],
                                'until': rel['until'],
                                'who': rel['who'],
                                'with': svg._id}
                        if not relkey(rrel) in vgroup_rlut:
                                logging.info("sofa: adding %s to %s" % (
                                        id2name[rrel['who']], str(svg.name)))
                                Es.rcol.insert(rrel)
                        else:
                                del vgroup_rlut[relkey(rrel)]
        # Check which relations to vgroups are unaccounted for and thus are to
        # be removed.
        for relkey in vgroup_rlut:
                logging.info("removing superfluous %s -> %s (%s)" % (
                        id2name[relkey[0]], id2name.get(relkey[2]),
                        id2name.get(relkey[1])))

def _create_yeargroup(g, year, name, tags, groups, id2name):
        n = {'types': ['group','tag'],
             'tags': [tags['!virtual-group']],
             'virtual': {
                     'type': 'year-group',
                     'group': g._id,
                     'year': year},
             'names': [name],
             'humanNames': [{
                     'name': name,
                     'human': unicode(g.humanName) + ' jaar ' + str(year)}]}
        n['_id'] = Es.ecol.insert(n)
        groups[name] = Es.entity(n)
        id2name[n['_id']] = name
