import protobufs.messages.hans_pb2 as hans_pb2

from django.conf import settings

from mailman.interfaces.listmanager import IListManager
from mailman.interfaces.domain import IDomainManager
from mailman.interfaces.styles import IStyle
from mailman.model.roster import RosterVisibility
from mailman.interfaces.mailinglist import (SubscriptionPolicy, DMARCMitigateAction)
from mailman.interfaces.action import Action
from mailman.interfaces.archiver import ArchivePolicy
from mailman.interfaces.styles import IStyleManager
from mailman.interfaces.usermanager import IUserManager
from mailman.core.initialize import initialize
from zope.component import getUtility
from zope.interface import implementer
import mailman.config
from mailman.app.lifecycle import create_list
from mailman.utilities.datetime import now
from mailman.database.transaction import transaction
from datetime import timedelta
from mailman.styles.base import (
    Announcement,
    BasicOperation,
    Bounces,
    Discussion,
    Identity,
    Moderation,
    Private,
    Public,
)


@implementer(IStyle)
class KNStyle:
    name = "kn"
    description = "Default KN Mailing List"
    def apply(self, mlist):
        Identity.apply(self, mlist)
        BasicOperation.apply(self, mlist)
        Bounces.apply(self, mlist)
        Private.apply(self, mlist)
        Discussion.apply(self, mlist)
        Moderation.apply(self, mlist)
        # Our custom settings
        # from: http://karpenoktem.com/wiki/WebCie:Mailinglist
        # send_reminders = 0
        mlist.digests_enabled = False
        mlist.send_welcome_message = False
        mlist.send_goodbye_message = False
        # max_message_size = 0
        mlist.subscription_policy = SubscriptionPolicy.confirm_then_moderate
        mlist.unsubscription_policy = SubscriptionPolicy.open
        mlist.member_roster_visibility = RosterVisibility.moderators
        # TODO set this on the `moderated` lists
        mlist.default_nonmember_action = Action.accept
        mlist.default_member_action = Action.accept
        mlist.require_explicit_destination = False
        # max_num_recipients = 0
        mlist.archive_policy = ArchivePolicy.private
        mlist.dmarc_mitigate_unconditionally = True
        mlist.preferred_language = 'nl'
        mlist.dmarc_mitigate_action = DMARCMitigateAction.munge_from
        mlist.autoresponse_grace_period = timedelta(days=1)

initialize()
style_manager = getUtility(IStyleManager)
style_manager.register(KNStyle())


def maillist_get_membership():
    ret = hans_pb2.GetMembershipResp()
    list_manager = getUtility(IListManager)
    for lst in list_manager:
        ret.membership[from_fqdn(lst.fqdn_listname)].emails.extend([x.address.email for x in lst.members.members])
    return ret

def to_fqdn(listname: str) -> str:
    return f"{listname}@{settings.LISTS_MAILDOMAIN}"

def from_fqdn(fqdn_listname: str) -> str:
    return fqdn_listname.removesuffix(f"@{settings.LISTS_MAILDOMAIN}")

def maillist_apply_changes(changes):
    user_manager = getUtility(IUserManager)
    list_manager = getUtility(IListManager)
    domain_manager = getUtility(IDomainManager)
    # print(changes)
    with transaction():
        if settings.LISTS_MAILDOMAIN not in domain_manager:
            domain_manager.add(settings.LISTS_MAILDOMAIN)
        for createReq in changes.create:
            ml = create_list(to_fqdn(createReq.name), [settings.MAILMAN_DEFAULT_OWNER.replace("localhost", "localhost.")], style_name="kn")
            ml.display_name = createReq.humanName
        for listname in changes.add:
            ml = list_manager.get(to_fqdn(listname))
            for em in changes.add[listname].emails:
                address = user_manager.get_address(em)
                if address is None:
                    user = user_manager.create_user(em)
                    address = list(user.addresses)[0]
                    address.verified_on = now()
                ml.subscribe(address)
        for listname in changes.remove:
            ml = list_manager.get(to_fqdn(listname))
            for em in changes.remove[listname].emails:
                member = ml.members.get_member(em)
                if member:
                    member.unsubscribe()
