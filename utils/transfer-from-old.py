import _import

from kn.leden.models import (OldKnUser, OldKnGroup, OldSeat,
			     KnUser, KnGroup, Seat, Entity)

def main():
	entlut = dict()

	for i in Entity.objects.all():
		i.delete()
	for i in KnUser.objects.all():
		i.delete()
	for i in KnGroup.objects.all():
		i.delete()
	for i in Seat.objects.all():
		i.delete()
	
	for o in OldKnUser.objects.all():
		n = KnUser(user=o,
			   first_name=o.first_name,
			   last_name=o.last_name,
			   email=o.email,
			   dateOfBirth=o.dateOfBirth,
			   dateJoined=o.dateJoined,
			   addr_street=o.addr_street,
			   addr_number=o.addr_number,
			   addr_zipCode=o.addr_zipCode,
			   addr_city=o.addr_city,
			   gender=o.gender,
			   telephone=o.telephone,
			   studentNumber=o.studentNumber,
			   institute=o.institute,
			   study=o.study,
			   name=o.username)
		entlut[o.username] = n
		n.save()

	for o in OldKnGroup.objects.all():
		n = KnGroup(name=o.name,
			    group=o,
			    humanName=o.humanName,
			    genitive_prefix=o.genitive_prefix,
			    description=o.description,
			    isVirtual=o.isVirtual,
			    subscribeParentToML=o.subscribeParentToML)
		n.save()
		entlut[o.name] = n
		for c in o.user_set.all():
			n.children.add(entlut[c.username])
	
	for o in OldKnGroup.objects.all():
		n = entlut[o.name]
		for c in OldKnGroup.objects.filter(parent=o):
			n.children.add(entlut[c.name])
	
	for o in OldSeat.objects.all():
		n = Seat(humanName=o.humanName,
			 description=o.description,
			 group=entlut[o.group.name],
			 name = o.group.name + '-' + o.name,
			 isGlobal=o.isGlobal)
		n.save()
		n.children.add(entlut[o.user.username])

if __name__ == '__main__':
	main()
