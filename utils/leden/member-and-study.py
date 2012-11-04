import _import

import sys
import csv

import kn.leden.entities as Es

def main():
    writer = csv.writer(sys.stdout)
    writer.writerow(['gebruikersnaam',
                     'voornaam',
                     'achternaam',
                     'van',
                     'tot',
                     'instituut',
                     'studierichting',
                     'studentnummer'])
    leden = Es.by_name('leden').get_members()
    leden.sort(cmp=lambda x,y: cmp(str(x.name), str(y.name)))
    for m in leden:
        if not m.is_user:
            continue
        if not m.studies:
            writer.writerow([m.name, m.humanName])
            continue
        for study in m.studies:
            writer.writerow(
                    [str(m.name),
                     m.first_name.encode('utf-8'),
                     m.last_name.encode('utf-8'),
                     study['from'].date() if study['from'] else '',
                     study['until'].date() if study['until'] else '',
                     unicode(study['institute'].humanName),
                     unicode(study['study'].humanName),
                     study['number']])

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
