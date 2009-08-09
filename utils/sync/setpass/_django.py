import _import
from kn.leden.models import OldKnUser

def setpass(user, passwd):
	m = OldKnUser.objects.get(username=user)
	m.set_password(passwd)
	m.save()
