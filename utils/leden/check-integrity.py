# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import kn.leden.entities as Es

# Do some too-intensive-for-Giedo sanity checks on the database
# Currently, check for orphan relations.


def main():
    ids = Es.ids()

    id2name = Es.names_by_ids()

    for r in Es.rcol.find():
        ok = True
        for a in ('who', 'with', 'from', 'until', 'how'):
            if a not in r:
                print(r['_id'], 'missing attribute', a)
                ok = False
        if not ok:
            continue
        if (r['who'] not in ids or r['with'] not in ids or (
                r['how'] is not None and r['how'] not in ids)):
            print(r['_id'], id2name.get(r['who'], r['who']),
                  id2name.get(r['with'], r['with']),
                  id2name.get(r['how'], r['how']))


if __name__ == '__main__':
    main()
