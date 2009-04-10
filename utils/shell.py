import _import
import Mailman.MailList
from kn.leden.models import Seat, KnGroup, KnUser, Alias

#
# Very short helper functions for trivial tasks
#

def cadd(commission, user):
	""" Add <user> to <commission> """
	KnGroup.objects.get(name=commission).user_set.add(KnUser.objects.get(username=user))

def sadd(commission, seat, user):
	""" Creates the seat <seat> for <commission> with <user> """
	s = Seat(name=seat,
		 humanName=seat.capitalize(),
		 user=KnUser.objects.get(username=user),
		 group=KnGroup.objects.get(name=commission),
		 description=seat)
	s.save()

def aadd(source, target):
	""" Creates the alias <source> -> <target> """
	a = Alias(source=source, target=target)
	a.save()

def u(username):
	""" Gets the <KnUser> with username <username> """
	return KnUser.objects.get(username=username)

def g(name):
	""" Gets the <KnGroup> with name <name> """
	return KnGroup.objects.get(name=name)

def ml(name):
	""" Gets the Mailman.MailList.MailList object for the list
		<name>. (Unlocked) """
	return Mailman.MailList.MailList(name, False)

def setgp(name, parent):
	""" Sets the parent of <name> to <parent> """
	gr = g(name)
	gr.parent = g(parent)
	gr.save()
