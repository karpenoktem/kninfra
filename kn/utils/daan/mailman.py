import logging
import os
from subprocess import call

from kn import settings

from kn.utils.mailman import import_mailman
import_mailman()
from Mailman import Utils, MailList, UserDesc, Errors, mm_cfg

def apply_mailman_changes(daan, changes):
        mlo = {}
        def ensure_opened(l):
                if l in mlo:
                        return True
                try:
                        mlo[l] = MailList.MailList(l)
                        return True
                except Errors.MMUnknownListError:
                        logging.warn("mailman: could not open %s" % l)
                return False
        for name, humanName in changes['create']:
                newlist = os.path.join(settings.MAILMAN_PATH, 'bin/newlist')
                ret = call([newlist, '-q', name, settings.MAILMAN_DEFAULT_OWNER,
                                        settings.MAILMAN_DEFAULT_PASSWORD])
                if ret != 0:
                        logging.error("bin/newlist failed")
                        continue
                # Our custom settings
                # from: http://karpenoktem.com/wiki/WebCie:Mailinglist
                ensure_opened(name)
                ml = mlo[name]
                ml.send_reminders = 0
                ml.send_welcome_msg = False
                ml.max_message_size = 0
                ml.subscribe_policy = 3
                ml.unsubscribe_policy = 0
                ml.private_roster = 2
                ml.generic_nonmember_action = 0
                ml.require_explicit_destination = 0
                ml.max_num_recipients = 0
                ml.archive_private = 1
        try:
                for l in changes['add']:
                        if not ensure_opened(l):
                                continue
                        for em in changes['add'][l]:
                                pw = Utils.MakeRandomPassword()
                                desc = UserDesc.UserDesc(em, '', pw, False)
                                mlo[l].ApprovedAddMember(desc, False, False)
                for l in changes['remove']:
                        if not ensure_opened(l):
                                continue
                        for em in changes['remove'][l]:
                                mlo[l].ApprovedDeleteMember(em,
                                        admin_notif=False, userack=False)
        finally:
                for ml in mlo.values():
                        ml.Save()
                        ml.Unlock()
