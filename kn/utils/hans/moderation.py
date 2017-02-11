import logging
import os

from django.conf import settings

from kn.utils.hans import mailman


def maillist_get_moderated_lists(hans):
    ret = {}
    for name in settings.MODED_MAILINGLISTS:
        try:
            ml = mailman.MailList.MailList(name, True)
        except mailman.Errors.MMUnknownListError:
            logging.warning("hans.moderation: list %s does not exist", name)
            continue
        try:
            ret[name] = {
                'modmode': ml.emergency,
                'real_name': ml.real_name,
                'description': ml.description,
                'queue': len(ml.GetHeldMessageIds())
            }
        finally:
            ml.Unlock()
    return ret


def maillist_activate_moderation(hans, name):
    try:
        ml = mailman.MailList.MailList(name, True)
    except mailman.Errors.MMUnknownListError:
        logging.warning("hans.moderation: list %s does not exist", name)
        return
    try:
        if ml.emergency:
            return
        ml.emergency = True
        ml.Save()
    finally:
        ml.Unlock()


def maillist_deactivate_moderation(hans, name):
    try:
        ml = mailman.MailList.MailList(name, True)
    except mailman.Errors.MMUnknownListError:
        logging.warning("hans.moderation: list %s does not exist", name)
        return
    try:
        if not ml.emergency:
            return
        ml.emergency = False
        for msg_id in ml.GetHeldMessageIds():
            ml.HandleRequest(msg_id, mailman.mm_cfg.APPROVE)
        ml.Save()
    finally:
        ml.Unlock()


def maillist_get_moderator_cookie(hans, name):
    try:
        ml = mailman.MailList.MailList(str(name), True)
    except mailman.Errors.MMUnknownListError:
        logging.warning("hans.moderation: list %s does not exist", name)
        return
    try:
        if ml.mod_password is None:
            ml.mod_password = mailman.Utils.sha_new(os.urandom(10)).hexdigest()
            ml.Save()
        return str(ml.MakeCookie(mailman.mm_cfg.AuthListModerator)).split(': ')
    finally:
        ml.Unlock()
