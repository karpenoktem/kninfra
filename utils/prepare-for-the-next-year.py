import _import  # noqa: F401

# Prepare for the coming change of "verenigingsjaar".

import argparse

import datetime

import kn.leden.entities as Es
from kn.base.conf import from_settings_import
from_settings_import("DT_MIN", "DT_MAX", globals())


def load_year_overrides():
    print 'loading year-overrides ...'
    year_overrides = {}
    for t in Es.bearers_by_tag_id(Es.id_by_name('!year-overrides'), _as=Es.Tag):
        year_overrides[(t._data['year-override']['type'],
                        t._data['year-override']['year'])] = t._id
    assert year_overrides
    years = frozenset([t[1] for t in year_overrides.keys()])
    min_year, max_year = min(years), max(years)
    return years, year_overrides, min_year, max_year


def create_year_overrides_for(year):
    """ Creates the year overrides for a certain year """
    parent_tag = Es.id_by_name('!year-overrides')
    Es.ecol.insert({
        'humanNames': [{u'human': u'Wel jaar {}'.format(year)}],
        'tags': [parent_tag],
        'types': ['tag'],
        'year-override': {'type': True, 'year': year}})
    Es.ecol.insert({
        'humanNames': [{u'human': u'Niet jaar {}'.format(year)}],
        'tags': [parent_tag],
        'types': ['tag'],
        'year-override': {'type': False, 'year': year}})


def main():
    parser = argparse.ArgumentParser(description="Prepare for the next year")
    parser.add_argument('--apply', action='store_true',
                    help=('Apply the changes.  By default the changes '
                          'are only displayed'))
    args = parser.parse_args()

    # Fetch year overrides
    while True:
        years, year_overrides, min_year, max_year = load_year_overrides()
        assert len(years) == max_year - min_year + 1  # year-override missing?
        current_year = Es.date_to_year(datetime.datetime.now())
        if current_year == max_year:
            print ' adding year-overrides for year', current_year + 1
            if args.apply:
                create_year_overrides_for(current_year + 1)
            continue
        break

    # Fetch ids of all current members
    leden_id = Es.id_by_name('leden')

    print 'If you became a member after june, you should be in the next year ...'
    for year in xrange(min_year+1, max_year+1):
        start_of_year = Es.year_to_range(year)[0]
        informal_start = start_of_year - datetime.timedelta(3*365/12)
        for rel in Es.rcol.find({'with': leden_id,
                                 'from': {'$gt': informal_start,
                                          '$lt': start_of_year}}):
            if year_overrides[(False, year-1)] in rel.get('tags', ()):
                continue
            if 'tags' not in rel:
                rel['tags'] = []
            rel['tags'].append(year_overrides[(False, year-1)])
            print ' ', Es.by_id(rel['who']).name, '-'+str(year-1)
            if args.apply:
                Es.rcol.save(rel)

    print 'Any relation that starts near the change of year, should start'
    print 'exactly on the change of year ...'
    for year in xrange(min_year+1, max_year+1):
        start_of_year = Es.year_to_range(year)[0]
        window = datetime.timedelta(1, 12*60*60)
        for rel in Es.rcol.find({'from': {'$gt': start_of_year - window,
                                          '$lt': start_of_year + window}}):
            if rel['from'] == start_of_year:
                continue
            how = Es.by_id(rel['how'])
            print ' {} {} (as {}): {} -> {}'.format(unicode(Es.by_id(rel['who'])),
                            str(Es.by_id(rel['with'])),
                            how._data['sofa_suffix'] if how else 'member',
                            rel['from'], start_of_year)
            if args.apply:
                rel['from'] = start_of_year
                Es.rcol.save(rel)

    print 'Any relation that ends near the change of year, should end'
    print 'exactly on the change of year ...'
    for year in xrange(min_year+1, max_year+1):
        start_of_year = Es.year_to_range(year)[0]
        end_of_year = Es.year_to_range(year)[0] - datetime.timedelta(0, 1)
        window = datetime.timedelta(1, 12*60*60)
        for rel in Es.rcol.find({'until': {'$gt': start_of_year - window,
                                          '$lt': start_of_year + window}}):
            if rel['until'] == end_of_year:
                continue
            how = Es.by_id(rel['how'])
            print ' {} {} (as {}): {} -> {}'.format(unicode(Es.by_id(rel['who'])),
                            str(Es.by_id(rel['with'])),
                            how._data['sofa_suffix'] if how else 'member',
                            rel['until'], end_of_year)
            if args.apply:
                rel['until'] = end_of_year
                Es.rcol.save(rel)

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
