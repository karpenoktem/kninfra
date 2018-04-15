# flake8: noqa

CHUCK_NORRIS_HIS_SECRET = '{{ pillar['secrets']['chucknorris'] }}'
SECRET_KEY = '{{ pillar['secrets']['django_secret_key'] }}'
ALLOWED_API_KEYS = ('{{ pillar['secrets']['apikey'] }}',)
MAILMAN_DEFAULT_PASSWORD = '{{ pillar['secrets']['mailman_default'] }}'
WIKI_MYSQL_SECRET = ('localhost', 'wiki',
                     '{{ pillar['secrets']['mysql_wiki'] }}', 'wiki')
FORUM_MYSQL_SECRET = ('localhost', 'forum',
                      '{{ pillar['secrets']['mysql_forum'] }}', 'forum')
WOLK_MYSQL_SECRET = ('localhost', 'wolk',
                     '{{ pillar['secrets']['mysql_wolk'] }}', 'wolk')
LDAP_PASS = '{{ pillar['secrets']['ldap_daan'] }}'
DOMAINNAME = '{{ grains['fqdn'] }}'
INFRA_UID = 2000  # Keep in synch. with kninfra.sls

from kn.defaultSettings import defaultSettings  # noqa: E402

defaultSettings(globals())

LDAP_USER = 'cn=daan,' + LDAP_SUFFIX
MEDIAWIKI_PATH = '/var/lib/mediawiki'
