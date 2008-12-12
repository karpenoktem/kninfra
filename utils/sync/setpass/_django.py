import _import
from kn.leden.models import KnUser

def setpass(user, passwd):
	m = KnUser.objects.get(username=user)
	m.set_password(passwd)
	m.save()
