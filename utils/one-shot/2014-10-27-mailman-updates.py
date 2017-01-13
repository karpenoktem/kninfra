# vim: et:sta:bs=2:sw=4:
import _import

from django.conf import settings
from kn.utils.mailman import import_mailman

import_mailman()
from Mailman.Utils import list_names
from Mailman.MailList import MailList


def main():
    url = 'https://%s/mailman/' % settings.MAILDOMAIN
    for x in list_names():
        ml = MailList(x, True)
        try:
            changed = False
            if ml.host_name != settings.LISTS_MAILDOMAIN:
                print 'Updating host_name of %s (was %s)' % (x, ml.host_name)
                ml.host_name = settings.LISTS_MAILDOMAIN
                changed = True
            if ml.from_is_list != 1:
                print 'Updating from_is_list of %s' % x
                ml.from_is_list = 1
                changed = True
            if ml.web_page_url != url:
                print 'Updating url_host of %s (was %s)' % (x, ml.web_page_url)
                ml.web_page_url = url
                changed = True
            # if changed:
            #    print 'Saving %s' % x
            #    ml.Save()
        finally:
            ml.Unlock()

if __name__ == '__main__':
    main()
