import _import

from common import *
from kn.leden.models import OldKnUser
import sys
import subprocess

def main():
	user = OldKnUser.objects.get(username=sys.argv[1])

	subprocess.call(['convert', '-resize', '200x', sys.argv[2],
			 'jpg:/var/django/kn/storage/smoelen/%s.jpg' % \
					 user.username])

if __name__ == '__main__':
	main()
