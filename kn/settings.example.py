# Example of settings.py.

import os

from kn.defaultSettings import defaultSettings  # noqa: E402

#
# You MUST change
#

CHUCK_NORRIS_HIS_SECRET = 'CHANGE ME'
SECRET_KEY = 'CHANGE ME'
ALLOWED_API_KEYS = ('CHANGE ME',)
MAILMAN_DEFAULT_PASSWORD = 'CHANGE ME'

#
# You might want to set one of the following.
# See defaultSettings.py for more settings.
# These should be of the form ('host', 'user', 'password', 'db')
# WIKI_MYSQL_SECRET = ('localhost', 'wiki', 'CHANGE ME', 'wiki')
# FORUM_MYSQL_SECRET = ('localhost', 'punbb', 'CHANGE ME', 'punbb')
# PHOTOS_MYSQL_SECRET = ('localhost', 'fotos', 'CHANGE ME', 'fotos')
# LDAP_PASS = 'CHANGE_ME'
# DOMAINNAME = 'karpenoktem.nl'
INFRA_HOME = os.environ['HOME']
INFRA_REPO = os.path.join(os.path.dirname(__file__), "../")

#
# Do not remove the following
#

defaultSettings(globals())

# vim: et:sta:bs=2:sw=4:
