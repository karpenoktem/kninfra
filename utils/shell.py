import _import
import Mailman.MailList
from kn.leden.models import OldSeat, OldKnGroup, OldKnUser, Alias

#
# Very short helper functions for trivial tasks
#

def cadd(commission, user):
	""" Add <user> to <commission> """
	OldKnGroup.objects.get(name=commission).user_set.add(OldKnUser.objects.get(username=user))

def sadd(commission, oldseat, user):
	""" Creates the oldseat <oldseat> for <commission> with <user> """
	s = OldSeat(name=oldseat,
		 humanName=oldseat.capitalize(),
		 user=OldKnUser.objects.get(username=user),
		 group=OldKnGroup.objects.get(name=commission),
		 description=oldseat)
	s.save()

def aadd(source, target):
	""" Creates the alias <source> -> <target> """
	a = Alias(source=source, target=target)
	a.save()

def u(username):
	""" Gets the <OldKnUser> with username <username> """
	return OldKnUser.objects.get(username=username)

def g(name):
	""" Gets the <OldKnGroup> with name <name> """
	return OldKnGroup.objects.get(name=name)

def ml(name):
	""" Gets the Mailman.MailList.MailList object for the list
		<name>. (Unlocked) """
	return Mailman.MailList.MailList(name, False)

def setgp(name, parent):
	""" Sets the parent of <name> to <parent> """
	gr = g(name)
	gr.parent = g(parent)
	gr.save()
