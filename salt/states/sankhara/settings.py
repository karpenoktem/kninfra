# flake8: noqa

{% if grains['vagrant'] %}
ALLOWED_HOSTS = ['*']
{% endif %}

CHUCK_NORRIS_HIS_SECRET = '{{ pillar['secrets']['chucknorris'] }}'
SECRET_KEY = '{{ pillar['secrets']['django_secret_key'] }}'
MAILMAN_DEFAULT_PASSWORD = '{{ pillar['secrets']['mailman_default'] }}'
WIKI_MYSQL_SECRET = ('localhost', 'giedo',
                     '{{ pillar['secrets']['mysql_giedo'] }}', 'wiki')
# WOLK_MYSQL_SECRET = ('localhost', 'giedo',
#                        '{{ pillar['secrets']['mysql_giedo'] }}', 'wolk')
LDAP_PASS = '{{ pillar['secrets']['ldap_infra'] }}'
DOMAINNAME = '{{ grains['fqdn'] }}'
INFRA_UID = 2000  # Keep in synch. with kninfra.sls
SCHEME = 'http'

from kn.defaultSettings import defaultSettings  # noqa: E402

defaultSettings(globals())

MEDIAWIKI_PATH = '/var/lib/mediawiki'
