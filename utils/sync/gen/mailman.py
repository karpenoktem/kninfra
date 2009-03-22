import Mailman
from common import *
import Mailman.Utils
import Mailman.MailList
from kn.leden.models import KnUser, KnGroup, Seat, Alias


def sync_mailman():
	mls = set(Mailman.Utils.list_names())
	coms = set()
	for com in KnGroup.objects.filter(isVirtual=False):
		coms.add(com.name)
		if not com.name in mls:
			print "mailman create %s" % com
			continue
		m = Mailman.MailList.MailList(com.name, lock=False)
		accounted = set()
		for user in com.user_set.all():
			email = "%s@%s" % (user, DOMAIN)
			accounted.add(email)
			if not email in m.members:
				print "mailman subscribe %s %s" % (com.name, email)
		if com.subscribeParentToML:
			email = com.parent.get_primary_email()
			accounted.add(email)
			if not email in m.members:
				print "mailman subscribe %s %s" % (com.name, email)
		for member, dummy in m.members.iteritems():
			if not member in accounted:
				print "mailman unsubscribe %s %s" % (com.name, member)
	for ml in mls:
		if not ml in coms:
			print "warn STRAY mailinglist %s" % ml 

