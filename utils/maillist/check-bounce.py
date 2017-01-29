import _import  # noqa: F401
from kn.utils.mailman import import_mailman

import_mailman()
import Mailman.MailList  # noqa: E402
import Mailman.Utils  # noqa: E402


def main():
    for name in Mailman.Utils.list_names():
        ml = Mailman.MailList.MailList(name, lock=False)
        if ml.bounce_info:
            print(name, ml.bounce_info)


if __name__ == '__main__':
    main()

# vim: et:sta:bs=2:sw=4:
