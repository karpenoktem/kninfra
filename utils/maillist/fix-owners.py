# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

import argparse

from kn.utils.hans.mailman import MailList, Utils
from django.conf import settings

ALLOWED_OWNERS = ['wortel@karpenoktem.nl',
                  'secretaris@karpenoktem.nl']


def main(do=False):
    expected_pw = Utils.sha_new(settings.MAILMAN_DEFAULT_PASSWORD).hexdigest()
    for x in Utils.list_names():
        ml = MailList.MailList(x, True)
        try:
            changed = False
            if ml.moderator and ml.moderator[0] == 'secretaris@karpenoktem.nl':
                if ml.password != expected_pw:
                    ml.password = expected_pw
                    print('Updating moderator password on %s' % x)
                    changed = True
            for o in ml.owner:
                if o not in ALLOWED_OWNERS:
                    print('Removing %s from %s' % (o, x))
                    ml.owner.remove(o)
                    changed = True
            if not ml.owner:
                ml.owner.append(ALLOWED_OWNERS[0])
                changed = True
            if changed and do:
                ml.Save()
        finally:
            ml.Unlock()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fix maillist moderators')
    parser.add_argument('--apply', action='store_true', help='apply changes')
    args = parser.parse_args()
    main(args.apply)
