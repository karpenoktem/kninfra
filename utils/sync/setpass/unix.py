from subprocess import call
import crypt
from common import pseudo_randstr
from kn.settings import SYSTEM_USERMOD_PATH

def setpass(user, password):
	crypthash = crypt.crypt(password, pseudo_randstr(2))
	call([SYSTEM_USERMOD_PATH, '-p', crypthash, user])
