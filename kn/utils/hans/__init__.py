from __future__ import absolute_import

import logging
import threading

from django.conf import settings

from kn.utils.hans.moderation import (maillist_activate_moderation,
                                      maillist_deactivate_moderation,
                                      maillist_get_moderated_lists)
from kn.utils.hans.sync import maillist_apply_changes, maillist_get_membership
from kn.utils.whim import WhimDaemon


class Hans(WhimDaemon):

    def __init__(self):
        super(Hans, self).__init__(settings.HANS_SOCKET)
        self.mailman_lock = threading.Lock()

    def handle(self, d):
        if d['type'] == 'maillist-get-membership':
            return maillist_get_membership(self)
        elif d['type'] == 'maillist-apply-changes':
            with self.mailman_lock:
                return maillist_apply_changes(self, d['changes'])
        elif d['type'] == 'maillist-get-moderated-lists':
            with self.mailman_lock:
                return maillist_get_moderated_lists(self)
        elif d['type'] == 'maillist-activate-moderation':
            with self.mailman_lock:
                return maillist_activate_moderation(self, d['name'])
        elif d['type'] == 'maillist-deactivate-moderation':
            with self.mailman_lock:
                return maillist_deactivate_moderation(self, d['name'])
        else:
            logging.warn("Unknown type {!r}".format(d['type']))


# vim: et:sta:bs=2:sw=4:
