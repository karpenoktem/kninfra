import sys

def ugetpass(prompt):
	sys.stdout.write(prompt)
	return sys.stdin.readline().rstrip("\n")
