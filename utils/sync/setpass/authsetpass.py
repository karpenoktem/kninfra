#!/usr/bin/env python
import sys
import crypt
import spwd
import common
import os
import setpass
import helpers

def main():
	if len(sys.argv) != 2:
		print "Usage: authsetpass.py <username>"
		sys.exit(-1)

	progname, username = sys.argv

	oldpasswd = helpers.ugetpass("Old password for %s:" % username)

	oldpasswd_cr = spwd.getspnam(username)[1] 

	if not oldpasswd_cr:
		print "User %s has no UNIX password!" % username
		sys.exit(11)

	if crypt.crypt(oldpasswd, oldpasswd_cr)!=oldpasswd_cr:
		print "Authentication failure"
		sys.exit(10)
	
	#os.execl("/usr/bin/python", "python", 
	#		"/root/utils/setpass/setpass.py", username)
	
	setpass.main()

if __name__ == '__main__':
	main()
