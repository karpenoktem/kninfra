import _import  # noqa: F401

from common import now

from django.utils import six

import kn.leden.entities as Es


def main():
    member_age = {}
    for rel in Es.query_relations(-1, Es.by_name('leden'), None,
                                  None, deref_who=True):
        if not rel['from']:
            rel['from'] = Es.DT_MIN
        if rel['who'] not in member_age:
            member_age[rel['who']] = Es.DT_MAX
        member_age[rel['who']] = rel['from']
    le = []
    for m, age in six.iteritems(member_age):
        if not m.dateOfBirth:
            continue
        print((age - m.dateOfBirth).days / 365.242, six.text_type(m.name))
        le.append((age - m.dateOfBirth).days / 365.242)
    print('avg', sum(le) / len(le))
    print('med', sorted(le)[len(le) / 2])
    print('1st', sorted(le)[len(le) / 4 * 2])
    print('3rd', sorted(le)[len(le) / 4 * 3])
    print('min', min(le))
    print('max', max(le))


def main3():
    member_age = {}
    for rel in Es.query_relations(-1, Es.by_name('leden'), None,
                                  None, deref_who=True):
        if rel['who'] not in member_age:
            member_age[rel['who']] = 0
        member_age[rel['who']] = max(member_age[rel['who']],
                                     (now() - rel['from']).days / 365.0)

    # for comm in Es.by_name('comms').get_bearers():
    for comm in [Es.by_name('draai')]:
        print(six.text_type(comm.humanName))
        members = [(m, member_age.get(m)) for m in comm.get_members()]
        members.sort(key=lambda x: x[1])
        for member in members:
            print(" %-20s%.2f" % (six.text_type(member[0].name),
                                  member[1] if member[1] else -1))


def main2():
    rels = list(Es.query_relations(-1,
                                   Es.by_name('comms').get_bearers(),
                                   None,
                                   now(),
                                   deref_who=True,
                                   deref_with=True))
    lut = {}
    for rel in rels:
        if rel['from'] is None:
            rel['from'] = Es.DT_MIN
        if not rel['with'] in lut:
            lut[rel['with']] = {}
        v = (now() - rel['from']).days / 365.0
        if rel['who'] not in lut[rel['with']] or \
                lut[rel['with']][rel['who']] > v:
            lut[rel['with']][rel['who']] = v

    pairs = lut.items()
    for comm, members in pairs:
        print(six.text_type(comm.humanName))
        mpairs = members.items()
        mpairs.sort(key=lambda x: x[1])
        for member, time in mpairs:
            print(' %-20s%.2f' % (member.name, time))


if __name__ == '__main__':
    main3()

# vim: et:sta:bs=2:sw=4:
