import _import  # noqa: F401

import sys
import csv

import kn.leden.entities as Es

from django.utils import six


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
    leden.sort(key=lambda x: str(x.name))
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
                 six.text_type(study['institute'].humanName),
                 six.text_type(study['study'].humanName),
                 study['number']])


if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
