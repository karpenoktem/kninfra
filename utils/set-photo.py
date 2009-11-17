import _import

from common import *
import sys
from kn.leden.models import OldKnUser
import subprocess

user = OldKnUser.objects.get(username=sys.argv[1])

subprocess.call(['convert', '-resize', '200x', sys.argv[2], 'jpg:/var/django/kn/storage/smoelen/%s.jpg' % user.username])
