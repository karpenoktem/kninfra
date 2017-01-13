import _import  # noqa: F401

""" Adds old members to oud """

import kn.leden.entities as Es


def main():
    oud = Es.by_name('oud')
    cur_leden, old_leden = Es.by_name('leden').get_current_and_old_members()
    cur_oud, old_oud = oud.get_current_and_old_members()
    for m in old_leden - old_oud - cur_oud:
        print m.name

        Es.rcol.insert({'who': Es._id(m),
                       'with': Es._id(oud),
                       'how': None,
                       'from': Es.now(),
                       'until': None})

if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
