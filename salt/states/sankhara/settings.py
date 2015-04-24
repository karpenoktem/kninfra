import datetime
import locale

# Base Django settings
# ############################################################

ADMINS = (
    ('Bas Westerbaan', 'bas@karpenoktem.nl'),
    ('Jille Timmermans', 'jille@karpenoktem.nl'),
    ('Bram Westerbaan', 'bramw@karpenoktem.nl'),
)

DATABASES = {'default': {}} # We do not use Django's DB abstraction
MANAGERS = ADMINS
TIME_ZONE = 'Europe/Amsterdam'
LANGUAGE_CODE = 'nl-NL'
SITE_ID = 1
USE_I18N = True
MEDIA_ROOT = '/home/infra/repo/media/'
MEDIA_URL = '/djmedia'
DEFAULT_FROM_EMAIL = 'Karpe Noktems ledenadministratie <root@{{ grains['fqdn'] }}>'

# Globally set locale
try:
    locale.setlocale(locale.LC_ALL, 'nl_NL.UTF-8')
except locale.Error:
    import logging
    logging.warn('Failed to set locale')

ROOT_URLCONF = 'kn.urls'
TEMPLATE_LOADERS = (
    ('kn.base.template.SlashNewlineStrippingTemplateLoader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'kn.leden.giedo.SyncStatusMiddleware',
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'kn.leden',
    'kn.poll', # XXX Not yet converted to Mongo
    'kn.subscriptions',
    'kn.browser',
    'kn.reglementen',
    'kn.base',
    'kn.moderation',
    'kn.fotos',
    'kn.barco',
    'kn.planning',
    'kn.static',
    'kn.agenda',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "kn.base.context_processors.base_url",
)
TEMPLATE_DIRS = ()
AUTHENTICATION_BACKENDS = (
    'kn.leden.auth.MongoBackend',
)
SESSION_ENGINE = 'kn.leden.sessions'
LOGIN_REDIRECT_URL='/smoelen/'
CACHE_BACKEND = 'locmem:///'

# required to get it running under FastCGI with LightTPD
FORCE_SCRIPT_NAME=''

# Our FILE_STORAGE
STORAGE_ROOT = '/home/infra/storage'
STORAGE_URL = '/djmedia/storage'
DEFAULT_FILE_STORAGE = 'kn.base.storage.OurFileSystemStorage'

# Application settings
# ############################################################
# smoelen
BASE_URL = 'https://{{ grains['fqdn'] }}'
ABSOLUTE_MEDIA_URL = BASE_URL + MEDIA_URL
SMOELEN_PHOTOS_PATH = 'smoelen'
SMOELEN_WIDTH = 300
SMOELEN_HEIGHT = 300
EXTERNAL_URLS = {
    'fotos-pdn': 'https://{{ grains['fqdn'] }}/fotos/index.php?album=pdn',
    'fotos':     'https://{{ grains['fqdn'] }}/fotos/',
    'stukken':   'https://{{ grains['fqdn'] }}/groups/leden/',
    'wiki':      'https://{{ grains['fqdn'] }}/wiki',
    'wiki-home': 'https://{{ grains['fqdn'] }}/wiki/Hoofdpagina',
    'forum':     'https://{{ grains['fqdn'] }}/forum/',
}

GOOGLE_CALENDAR_IDS = {
    'kn':   'vssp95jliss0lpr768ec9spbd8@group.calendar.google.com',
    'zeus': 'a9jl7tuhqg7oe8stapcu9uhvk8@group.calendar.google.com',
}

# moderation & mailman
MAILDOMAIN = '{{ grains['fqdn'] }}'
LISTS_MAILDOMAIN = 'lists.{{ grains['fqdn'] }}'
MODED_MAILINGLISTS = ['discussie', 'in', 'uit', 'test']
MODERATORS_GROUP = 'moderators'
MOD_UI_URI = '/mailman/admindb/%s'
MOD_RENEW_INTERVAL = datetime.timedelta(0, 15*60)
MOD_DESIRED_URI_PREFIX = 'https://{{ grains['fqdn'] }}'
MAILMAN_PATH = '/var/lib/mailman'
MEDIAWIKI_PATH = '/srv/karpenoktem.nl/htdocs/mediawiki'
MAILMAN_DEFAULT_OWNER = 'wortel@{{ grains['fqdn'] }}'

# db
MONGO_HOST = 'localhost'
MONGO_DB = 'kn'

# db constants
DT_MIN = datetime.datetime(2004,8,31)
DT_MAX = datetime.datetime(5004,9,1)

# synchronisation
GIEDO_SOCKET = '/var/run/infra/S-giedo'
DAAN_SOCKET = '/var/run/infra/S-daan'
CILIA_SOCKET = '/var/run/infra/S-cilia'

USERNAME_CHARS = 'qwertyuiopasdfghjklzxcvbnm123456789-'

POSTFIX_VIRTUAL_MAP = '/etc/postfix/virtual/kninfra_maps'
POSTFIX_SLM_MAP = '/etc/postfix/virtual/kninfra_slm_maps'
INFRA_UID = 1002

PHOTOS_DIR = '/var/fotos'
PHOTOS_CACHE_DIR = '/var/cache/fotos'
USER_DIRS = '/mnt/phassa/home/'

LDAP_HOST = 'localhost'
LDAP_BASE = 'ou=users,dc=karpenoktem,dc=nl'
LDAP_USER = 'cn=giedo,dc=karpenoktem,dc=nl'
WOLK_USER = 'wolk'
WOLK_PATH = '/var/www/wolk'
WOLK_DATA_PATH = '/mnt/phassa/wolk'

# VPN related
# ############################################################
VPN_COMMONNAME_POSTFIX = '.vpn.karpenoktem.nl'
VPN_KEYSTORE = '/home/infra/vpnkeys'
VPN_INSTALLER_PATH = 'openvpn'
VPN_INSTALLER_REPOS = '/home/infra/openvpn'

# Debug settings
# ############################################################
DEBUG = True
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ['195.169.216.49'] # bas

# Secrets
# ############################################################
SECRET_KEY = 'CHANGE ME'
MAILMAN_DEFAULT_PASSWORD = 'CHANGE ME'

WIKI_MYSQL_SECRET = ('localhost', 'wiki',
                        '{{ pillar['secrets']['mysql_wiki'] }}', 'wiki')
FORUM_MYSQL_SECRET = ('localhost', 'forum',
                        '{{ pillar['secrets']['mysql_forum'] }}', 'forum')
WOLK_MYSQL_SECRET = ('localhost', 'wolk',
                        '{{ pillar['secrets']['mysql_wolk'] }}', 'wolk')
ALLOWED_API_KEYS = ('{{ pillar['secrets']['apikey'] }}',)
CHUCK_NORRIS_HIS_SECRET = '{{ pillar['secrets']['chucknorris'] }}'
VILLANET_SECRET_API_KEY = '' # CHANGE ME
DEFAULT_FROM_EMAIL = ('Karpe Noktems ledenadministratie '+
                        '<root@{{ grains['fqdn'] }}>')
LDAP_PASS = None # 'CHANGE ME'

# vim: et:sta:bs=2:sw=4: