import re
import os
import sys
import unix
import wiki
import forum
import common
import photos
import _django
import helpers
import zeusForum

USERRE = re.compile("^[a-z0-9]+$")
PASSRE = re.compile("^[a-zA-Z0-9`~!@#$%^&*()-_=+[{\\]}\\\\|;:\"'<,>.?/]+$")


def main():
	if len(sys.argv) != 2:
		print "Usage: setpass.py <username>"
		sys.exit(-1)
	progname, user= sys.argv
	os.chdir(os.path.abspath(os.path.dirname(progname)))
	password = helpers.ugetpass("New password for %s:" % user)
	if not USERRE.match(user):
		print "Username isn't sane"
		sys.exit(-2)
	if not PASSRE.match(password):
		print "Password isn't sane"
		sys.exit(-3)
	for i in [unix, zeusForum, forum, _django, wiki]:
		i.setpass(user, password)

	
if __name__ == '__main__':
	main()
