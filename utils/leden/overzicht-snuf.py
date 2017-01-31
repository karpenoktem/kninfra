import _import  # noqa: F401
import csv
import datetime
import sys

import kn.leden.entities as Es


def main():
    writer = csv.writer(sys.stdout)
    writer.writerow(['gebruikersnaam',
                     'voornaam',
                     'achternaam',
                     'instituut',
                     'studierichting',
                     'studentnummer'])
    leden = Es.by_name('leden').get_members()
    leden.sort(cmp=lambda x, y: cmp(str(x.name), str(y.name)))
    now = datetime.datetime.now()
    for m in leden:
        if not m.is_user:
            continue
        ok = False
        if m.studies:
            for study in m.studies:
                if ((study['from'] and study['from'] > now)
                        or (study['until'] and study['until'] < now)):
                    continue
                writer.writerow(
                    [str(m.name),
                     m.first_name.encode('utf-8'),
                     m.last_name.encode('utf-8'),
                     unicode(study['institute'].humanName).encode('utf-8'),
                     unicode(study['study'].humanName).encode('utf-8'),
                     study['number']])
                ok = True
                break
        if not ok:
            writer.writerow([str(m.name),
                             m.first_name.encode('utf-8'),
                             m.last_name.encode('utf-8')])
            continue


if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
