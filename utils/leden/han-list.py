# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import kn.leden.entities as Es


def main():
    leden = frozenset(Es.by_name('leden').get_members())
    han = Es.by_id('4e6fcc85e60edf3dc0000015')
    for m in sorted(Es.by_institute(han), key=lambda x: str(x.name)):
        if m not in leden:
            continue
        ok = False
        for study in m.studies:
            if study['institute'] != han:
                continue
            if study['until'] is None or study['until'] >= Es.now():
                ok = True
        print "%-30s %-10s %s" % (m.full_name, study['number'],
                        unicode(study['study'].humanName))

if __name__ == '__main__':
    main()
