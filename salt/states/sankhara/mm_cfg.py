from Defaults import *

MAILMAN_SITE_LIST = 'mailman'

# TODO https
DEFAULT_URL_PATTERN = 'http://%s/mailman/'
IMAGE_LOGOS         = '/mailman-icons/'

DEFAULT_EMAIL_HOST = 'lists.{{ grains['fqdn'] }}'
DEFAULT_URL_HOST   = '{{ grains['fqdn'] }}'

add_virtualhost(DEFAULT_URL_HOST, DEFAULT_EMAIL_HOST)

DEFAULT_SERVER_LANGUAGE = 'en'
USE_ENVELOPE_SENDER    = 0
DEFAULT_SEND_REMINDERS = 0
MTA = 'Postfix'
POSTFIX_STYLE_VIRTUAL_DOMAINS = ['lists.{{ grains['fqdn'] }}']
VIRTUAL_HOST_OVERVIEW = Off
DEB_LISTMASTER = 'wortel@{{ grains['fqdn'] }}'
DEFAULT_LIST_ADVERTISED = False

SITE_LOGO = '/mailman-icons/debianpowered.png' # bugfix
