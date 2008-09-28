import _import
from kn.leden.models import Seat, Commission, Member, Alias

#
# Very short helper functions for trivial tasks
#

def cadd(commission, user):
	""" Add <user> to <commission> """
	Commission.objects.get(name=commission).user_set.add(User.objects.get(username=user))

def sadd(commission, seat, user):
	""" Creates the seat <seat> for <commission> with <user> """
	s = Seat(name=seat,
		 humanName=seat.capitalize(),
		 member=Member.objects.get(username=user),
		 commission=Commission.objects.get(name=commission),
		 description=seat)
	s.save()

def aadd(source, target):
	""" Creates the alias <source> -> <target> """
	a = Alias(source=source, target=target)
	a.save()
