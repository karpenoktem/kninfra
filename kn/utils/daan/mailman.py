import logging

from kn.utils.mailman import import_mailman
import_mailman()
from Mailman import Utils, MailList, UserDesc, Errors

def apply_mailman_changes(daan, changes):
        mlo = {}
        def ensure_opened(l):
                if l in mlo:
                        return
                try:
                        mlo[l] = MailList.MailList(l)
                        return True
                except Errors.MMUnknownListError:
                        logging.warn("mailman: could not open %s" % l)
                return False
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
