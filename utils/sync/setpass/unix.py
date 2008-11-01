from subprocess import Popen, PIPE, call

def setpass(user, password):
	makepassword = Popen(['makepasswd', '--clearfrom=-', '--crypt'],
			stdin=PIPE, stdout=PIPE)
	makepassword.stdin.write(password)
	makepassword.stdin.close()
	crypthash = makepassword.stdout.read().split(' ')[-1][:-1]
	call(['usermod', '-p', crypthash, user])
