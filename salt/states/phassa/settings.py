SECRET_KEY = '{{ pillar['secrets']['django_secret_key'] }}'
DOMAINNAME = '{{ grains['fqdn'] }}'

from kn.defaultSettings import defaultSettings
defaultSettings(globals())
