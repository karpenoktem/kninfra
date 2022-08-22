# Example of settings.py.
# this file should retain python2 compatibility until Hans is ported to python3

import os

from kn.defaultSettings import defaultSettings  # noqa: E402
from pathlib import Path

#
# You MUST change
#

CHUCK_NORRIS_HIS_SECRET = 'CHANGE ME'
SECRET_KEY = 'CHANGE ME'
MAILMAN_DEFAULT_PASSWORD = 'CHANGE ME'

#
# You might want to set one of the following.
# See defaultSettings.py for more settings.
# These should be of the form ('host', 'user', 'password', 'db')
# FORUM_MYSQL_SECRET = ('localhost', 'punbb', 'CHANGE ME', 'punbb')
# PHOTOS_MYSQL_SECRET = ('localhost', 'fotos', 'CHANGE ME', 'fotos')
# DOMAINNAME = 'karpenoktem.nl'
INFRA_HOME = os.environ['HOME']
INFRA_REPO = os.path.join(os.path.dirname(__file__), "../")

GIEDO_SOCKET = "/run/infra/giedo"

for varname, value in os.environ.items():
    if varname.startswith("KN_"):
        globals[varname[3:]] = value

# Do not remove the following
#

defaultSettings(globals())

# vim: et:sta:bs=2:sw=4:
