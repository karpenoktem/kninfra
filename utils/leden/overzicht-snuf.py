import _import  # noqa: F401

import sys
import csv
import datetime

import kn.leden.entities as Es

from django.utils.six import text_type


def main():
    writer = csv.writer(sys.stdout)
    writer.writerow(['gebruikersnaam',
                     'voornaam',
                     'achternaam',
                     'instituut',
                     'studierichting',
                     'studentnummer'])
    leden = Es.by_name('leden').get_members()
    leden.sort(key=lambda x: str(x.name))
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
                     text_type(study['institute'].humanName).encode('utf-8'),
                     text_type(study['study'].humanName).encode('utf-8'),
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
