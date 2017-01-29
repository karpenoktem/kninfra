import _import  # noqa: F401
import datetime  # noqa: F401

import kn.leden.entities as Es


def main():
    for n in []:
        e = Es.by_name(n)
        print n
        for rel in e.get_related(_from=Es.now(), until=Es.now()):
            grp = rel['with']
            if grp.is_virtual:
                continue
            if str(grp.name) == 'nibbana':
                continue
            if str(grp.name) == 'uilfest':
                continue
            print ' ' + str(grp.name)
            assert rel['until'] is None
            # Es.rcol.update({'_id': rel['_id']},
            #                {'$set': {'until': datetime.datetime(2015,8,31)}})


if __name__ == '__main__':
    main()
