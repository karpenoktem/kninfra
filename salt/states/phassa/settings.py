# flake8: noqa

SECRET_KEY = '{{ pillar['secrets']['django_secret_key'] }}'
DOMAINNAME = '{{ grains['fqdn'] }}'

from kn.defaultSettings import defaultSettings  # noqa: E402
defaultSettings(globals())
