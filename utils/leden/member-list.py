import _import # noqa: F401

import sys

import kn.leden.entities as Es


def main():
    now = Es.now()
    for n, r in enumerate(sorted(Es.query_relations(
            _with=Es.id_by_name('leden'), _from=now, until=now,
            deref_who=True),
                key=lambda r: r['from'])):
        print n+1, r['who'].humanName


if __name__ == '__main__':
    if sys.stdout.encoding is None:
        reload(sys)
        sys.setdefaultencoding('utf-8')
    main()

# vim: et:sta:bs=2:sw=4:
