
import _import

# Add the "not in year x" override if someone joined near the end of year x.
#               bas@kn.cx

import datetime

import kn.leden.entities as Es
from kn.leden.mongo import _id
from kn.settings import DT_MIN, DT_MAX

def main():
    # Fetch year overrides
    print 'loading year overrides ...'
    year_overrides = {}
    for t in Es.bearers_by_tag_id(Es.id_by_name('!year-overrides'), _as=Es.Tag):
        year_overrides[(t._data['year-override']['type'],
                        t._data['year-override']['year'])] = t._id
    assert year_overrides
    years = [t[1] for t in year_overrides.keys()]
    min_year, max_year = min(years), max(years)
    leden_id = Es.id_by_name('leden')
    print 'checking ...'
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
            print Es.by_id(rel['who']).name, year
            # UNCOMMENT the following line for the code to commit its
            #           changes.  Check the changes first!
            #Es.rcol.save(rel)

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
