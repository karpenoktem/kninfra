# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

from Mailman.MailList import MailList
from Mailman.Utils import list_names

ALLOWED_OWNERS = ['wortel@karpenoktem.nl',
                  'secretaris@karpenoktem.nl']


def main():
    for x in list_names():
        ml = MailList(x, True)
        try:
            changed = False
            for o in ml.owner:
                if o not in ALLOWED_OWNERS:
                    print 'Removing %s from %s' % (o, x)
                    ml.owner.remove(o)
                    changed = True
            if not ml.owner:
                ml.owner.append(ALLOWED_OWNERS[0])
                changed = True
            if changed:
                ml.Save()
        finally:
            ml.Unlock()


if __name__ == '__main__':
    main()
