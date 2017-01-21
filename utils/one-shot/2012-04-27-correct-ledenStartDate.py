import _import  # noqa: F401

# In the old administration, we only registered membership of `leden' rounded
# to years.  However, we kept the registration date separately.  In the
# conversion to Mongo, we have stored this registration date in
# user.temp.joined.  This script corrects the start-date of the relation with
# leden for users according to user.temp.joined.
# This script adds, where neccessary year-override-tags to the relations.
# This is, for instance, to prevent someone who joined in 2007-08-20 to
# be added to leden3.
#                       2012-04-27       bas@kn.cx

import datetime

import kn.leden.entities as Es


def main():
    year_overrides = dict()
    had = set()
    for t in Es.bearers_by_tag_id(Es.id_by_name('!year-overrides'), _as=Es.Tag):
        year_overrides[(t._data['year-override']['type'],
                        t._data['year-override']['year'])] = t._data['_id']
    for rel in sorted(Es.query_relations(-1, Es.id_by_name('leden'), None,
                                         None, None, True, False, False),
                      cmp=lambda x, y: cmp(x['from'], y['from'])):
        name = str(rel['who'].name)
        if name in had:
            continue
        if ('temp' not in rel['who']._data or
                'joined' not in rel['who']._data['temp']):
            had.add(name)
            continue
        joined = datetime.datetime.strptime(
                rel['who']._data['temp']['joined'], '%Y-%m-%d')
        if joined == rel['from']:
            had.add(name)
            continue
        joined_yr = Es.date_to_year(joined)
        from_yr = Es.date_to_year(rel['from'])
        if joined_yr == from_yr or joined_yr == 0:
            print name, rel['from'].date(), ' -> ', \
                                joined.date()
            rrel = Es.rcol.find({'_id': rel['_id']})[0]
            rrel['from'] = joined
            Es.rcol.save(rrel)
            had.add(name)
            continue
        if joined_yr == from_yr - 1:
            print name, rel['from'].date(), ' -> ', \
                                joined.date()
            rrel = Es.rcol.find({'_id': rel['_id']})[0]
            rrel['from'] = joined
            if 'tags' not in rrel:
                rrel['tags'] = []
            if not year_overrides[(False, joined_yr)] in rrel['tags']:
                rrel['tags'].append(year_overrides[(False, joined_yr)])
            Es.rcol.save(rrel)
            had.add(name)
            continue
        print 'MANUAL REVIEW: ', name, joined.date(), rel['from'].date()

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
