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
DOMAIN = '{{ grains['fqdn'] }}'

from defaultSettings import defaultSettings
defaultSettings(globals())
