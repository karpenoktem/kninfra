import logging
import os.path
import subprocess

from django.conf import settings

import kn.utils.hans.hans_pb2 as hans_pb2
from kn.utils.hans import mailman


def maillist_get_membership():
    ret = hans_pb2.GetMembershipResp()
    for list_name in mailman.Utils.list_names():
        lst = mailman.MailList.MailList(list_name, lock=False)
        ret.membership[list_name].emails.extend(lst.members)
    return ret


def maillist_apply_changes(changes):
    mlo = {}

    def ensure_opened(l):
        if l in mlo:
            return True
        try:
            mlo[l] = mailman.MailList.MailList(l)
            return True
        except mailman.Errors.MMUnknownListError:
            logging.warn("mailman: could not open %s" % l)
        return False
    for createReq in changes.create:
        newlist = os.path.join(settings.MAILMAN_PATH, 'bin/newlist')
        ret = subprocess.call([
            newlist,
            '-q',
            createReq.name,
            settings.MAILMAN_DEFAULT_OWNER,
            settings.MAILMAN_DEFAULT_PASSWORD])
        if ret != 0:
            logging.error("bin/newlist failed")
            continue
        # Our custom settings
        # from: http://karpenoktem.com/wiki/WebCie:Mailinglist
        ensure_opened(createReq.name)
        ml = mlo[createReq.name]
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
        ml.from_is_list = 1
    try:
        for l in changes.add:
            if not ensure_opened(l):
                continue
            for em in changes.add[l].emails:
                pw = mailman.Utils.MakeRandomPassword()
                desc = mailman.UserDesc.UserDesc(em, '', pw, False)
                mlo[l].ApprovedAddMember(desc, False, False)
        for l in changes.remove:
            if not ensure_opened(l):
                continue
            for em in changes.remove[l].emails:
                mlo[l].ApprovedDeleteMember(
                    em,
                    admin_notif=False,
                    userack=False
                )
    finally:
        for ml in mlo.values():
            ml.Save()
            ml.Unlock()
