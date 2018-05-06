import _import  # noqa: F401

import kn.leden.entities as Es

# Removes some empty entries from the database.
#               bas@kn.cx


def main():
    for e in Es.users():
        # Remove empty study entries
        if e._data['studies']:
            study = e._data['studies'][0]
            if (study['study'] is None and
                    study['number'] is None and
                    study['institute'] is None and
                    len(e._data['studies']) == 1):
                e._data['studies'] = []
                e.save()
        # Remove empty address entries
        if e._data['addresses']:
            address = e._data['addresses'][0]
            if (not address['street'] and
                    not address['city'] and
                    not address['number'] and
                    len(e._data['addresses']) == 1):
                e._data['addresses'] = []
                e.save()
        # Remove empty telephone entries
        if e._data['telephones']:
            address = e._data['telephones'][0]
            if (not address['number'] and
                    len(e._data['telephones']) == 1):
                e._data['telephones'] = []
                e.save()


if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
