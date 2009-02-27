import re
import sys
import unix
import forum
import photos
import _django

USERRE = re.compile("^[a-z0-9]+$")
PASSRE = re.compile("^[a-zA-Z0-9`~!@#$%^&*()-_=+[{\\]}\\\\|;:\"'<,>.?/]+$")

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print "Usage: setpass.py <username> <password>"
		sys.exit(-1)
	user, password = sys.argv[1:]
	if not USERRE.match(user):
		print "Username isn't sane"
		sys.exit(-2)
	if not PASSRE.match(password):
		print "Password isn't sane"
		sys.exit(-3)
	for i in [unix, photos, forum, _django]:
		i.setpass(user, password)
