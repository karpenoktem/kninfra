from subprocess import call
import crypt
from common import pseudo_randstr

def setpass(user, password):
	crypthash = crypt.crypt(password, pseudo_randstr(2))
	call(['/usr/sbin/usermod', '-p', crypthash, user])
