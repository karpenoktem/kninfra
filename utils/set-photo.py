# vim: et:sta:bs=2:sw=4:
import _import  # noqa: F401

from kn.leden.models import OldKnUser
from django.conf import settings
from os import path
import sys
import subprocess


def main(username, photo):
    user = OldKnUser.objects.get(username=username)
    subprocess.call(['convert', '-resize', '200x', photo,
                     "jpg:%s.jpg" % (path.join(settings.SMOELEN_PHOTOS_PATH,
                                               user.username))])

if __name__ == '__main__':
    if not len(sys.argv) == 3:
        print "python set-photo.py <username> <path-to-photo>"
        sys.exit(-1)
    main(*sys.argv[1:3])
