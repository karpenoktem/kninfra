from __future__ import absolute_import

import logging
import threading

from django.conf import settings

from kn.utils.hans.sync import maillist_apply_changes, maillist_get_membership
from kn.utils.whim import WhimDaemon


class Hans(WhimDaemon):

    def __init__(self):
        super(Hans, self).__init__(settings.HANS_SOCKET)
        self.mailman_lock = threading.Lock()

    def pre_mainloop(self):
        super(Hans, self).pre_mainloop()
        self.notify_systemd()

    def handle(self, d):
        if d['type'] == 'maillist-get-membership':
            return maillist_get_membership(self)
        elif d['type'] == 'maillist-apply-changes':
            with self.mailman_lock:
                return maillist_apply_changes(self, d['changes'])
        else:
            logging.warn("Unknown type {!r}".format(d['type']))


# vim: et:sta:bs=2:sw=4:
