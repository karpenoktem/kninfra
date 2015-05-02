# Default settings.  Change in settings.py.  See settings.example.py.
# ###################################################################

import datetime
import locale

# We want smart default. Eg: on a particular installation BASE_URL might be
# overwritten (default: karpenoktem.nl).  However, if it is, we want other
# defaults, which depend on BASE_URL, to use the overwritten BASE_URL.
# That is why defaultSettings() is executed *after* custom settings.
# To have a nice syntax, we use a small DEFAULTS helper class.

def defaultSettings(glbls):
    d = DEFAULTS(glbls)

    # Settings you must set.
    # ############################################################

    #CHUCK_NORRIS_HIS_SECRET = 'CHANGE ME'
    #SECRET_KEY = 'CHANGE ME'
    #ALLOWED_API_KEYS = ('CHANGE ME',)
    #MAILMAN_DEFAULT_PASSWORD = 'CHANGE ME'

    # You are very likely to override these
    # ############################################################
    d.VILLANET_SECRET_API_KEY = None
    # These should be of the form ('host', 'user', 'password', 'db')
    d.WIKI_MYSQL_SECRET = None
    d.FORUM_MYSQL_SECRET = None
    d.WOLK_MYSQL_SECRET = None

    d.LDAP_HOST = 'localhost'
    d.LDAP_BASE = 'ou=users,dc=karpenoktem,dc=nl'
    d.LDAP_USER = 'cn=daan,dc=karpenoktem,dc=nl'
    d.LDAP_PASS = None
    d.DOMAINNAME = 'karpenoktem.nl'

    # Settings you probably want to change
    # ############################################################

    d.INFRA_HOME = '/home/infra'
    d.INFRA_REPO = d.INFRA_HOME + '/repo'

    d.MEDIA_URL = '/djmedia/'
    d.STORAGE_URL = '/djmedia/storage'
    d.WOLK_DATA_PATH = '/mnt/phassa/srv/wolk'
    d.INFRA_UID = 1002

    d.SCHEME = 'https'

    # Maybe you want to change these
    # ############################################################

    d.MEDIA_ROOT = d.INFRA_REPO + '/media/'
    d.STORAGE_ROOT = d.INFRA_HOME + '/storage'
    d.GOOGLE_OAUTH2_KEY = d.INFRA_HOME + '/google-oauth-key.json'

    d.BASE_URL = d.SCHEME + '://' + d.DOMAINNAME
    d.PHOTOS_CACHE_DIR = '/var/cache/fotos'
    d.MAILDOMAIN = d.DOMAINNAME

    d.LISTS_MAILDOMAIN = 'lists.' + d.DOMAINNAME
    d.MAILMAN_PATH = '/var/lib/mailman'
    d.MAILMAN_DEFAULT_OWNER = 'wortel@'+d.MAILDOMAIN
    d.DEFAULT_FROM_EMAIL = 'Karpe Noktems ledenadministratie <root@%s>' \
                                    % d.MAILDOMAIN

    d.MONGO_HOST = 'localhost'
    d.MONGO_DB = 'kn'

    d.MODED_MAILINGLISTS = ['discussie', 'in', 'uit', 'test']
    d.MODERATORS_GROUP = 'moderators'
    d.MOD_UI_URI = '/mailman/admindb/%s'
    d.MOD_RENEW_INTERVAL = datetime.timedelta(0, 15*60)
    d.MOD_DESIRED_URI_PREFIX = d.SCHEME + '://www.' + d.DOMAINNAME

    d.MEDIAWIKI_PATH = '/srv/' + d.DOMAINNAME + '/htdocs/mediawiki'

    d.ADMINS = (
            ('Bas Westerbaan', 'bas@karpenoktem.nl'),
            ('Jille Timmermans', 'jille@karpenoktem.nl'),
            ('Bram Westerbaan', 'bramw@karpenoktem.nl'),
    )

    d.GIEDO_SOCKET = '/var/run/infra/S-giedo'
    d.DAAN_SOCKET = '/var/run/infra/S-daan'
    d.CILIA_SOCKET = '/var/run/infra/S-cilia'

    d.GOOGLE_CALENDAR_IDS = {
        'kn':   'vssp95jliss0lpr768ec9spbd8@group.calendar.google.com',
        'zeus': 'a9jl7tuhqg7oe8stapcu9uhvk8@group.calendar.google.com',
    }

    d.POSTFIX_VIRTUAL_MAP = '/etc/postfix/virtual/kninfra_maps'
    d.POSTFIX_SLM_MAP = '/etc/postfix/virtual/kninfra_slm_maps'

    d.PHOTOS_DIR = '/var/fotos'
    d.USER_DIRS = '/mnt/phassa/home/'

    d.VPN_COMMONNAME_POSTFIX = '.vpn.' + d.DOMAINNAME
    d.VPN_KEYSTORE = d.INFRA_HOME + '/vpnkeys'
    d.VPN_INSTALLER_STORAGE = d.STORAGE_ROOT + '/openvpn'
    d.VPN_INSTALLER_PATH = 'openvpn'
    d.VPN_INSTALLER_REPOS = d.INFRA_HOME + '/openvpn'

    d.INTERNAL_IPS = ['195.169.216.49'] # bas
    d.LOCALE = 'nl_NL.UTF-8'

    # You probably won't change this
    # ############################################################

    d.DATABASES = {'default': {}} # We do not use Django's DB abstraction
    d.CACHE_BACKEND = 'locmem:///'
    d.MANAGERS = d.ADMINS
    d.TIME_ZONE = 'Europe/Amsterdam'
    d.LANGUAGE_CODE = 'nl-NL'
    d.SITE_ID = 1
    d.USE_I18N = True


    d.ROOT_URLCONF = 'kn.urls'
    d.TEMPLATE_LOADERS = (
        ('kn.base.template.SlashNewlineStrippingTemplateLoader', (
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        )),
    )
    d.MIDDLEWARE_CLASSES = (
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'kn.leden.giedo.SyncStatusMiddleware',
    )
    d.INSTALLED_APPS = (
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'kn.leden',
            'kn.poll',
            'kn.subscriptions',
            'kn.browser',
            'kn.reglementen',
            'kn.base',
            'kn.moderation',
            'kn.planning',
            'kn.fotos',
            'kn.barco',
            'kn.static',
            'kn.agenda',
    )
    d.TEMPLATE_CONTEXT_PROCESSORS = (
            "django.contrib.auth.context_processors.auth",
            "django.core.context_processors.debug",
            "django.core.context_processors.i18n",
            "django.core.context_processors.media",
            "django.contrib.messages.context_processors.messages",
            "kn.base.context_processors.base_url",
    )
    d.TEMPLATE_DIRS = ()
    d.AUTHENTICATION_BACKENDS = (
            'kn.leden.auth.MongoBackend',
    )
    d.SESSION_ENGINE = 'kn.leden.sessions'
    d.LOGIN_REDIRECT_URL='/smoelen/'
    d.DEFAULT_FILE_STORAGE = 'kn.base.storage.OurFileSystemStorage'

    d.FORCE_SCRIPT_NAME=''

    d.SMOELEN_PHOTOS_PATH = 'smoelen'
    d.SMOELEN_WIDTH = 300
    d.SMOELEN_HEIGHT = 300

    d.EXTERNAL_URLS = {
        'stukken':   d.BASE_URL+'/groups/leden/',
        'wiki':      d.BASE_URL+'/wiki',
        'wiki-home': d.BASE_URL+'/wiki/Hoofdpagina',
        'forum':     d.BASE_URL+'/forum/',
    }

    d.DT_MIN = datetime.datetime(2004,8,31)
    d.DT_MAX = datetime.datetime(5004,9,1)

    d.USERNAME_CHARS = 'qwertyuiopasdfghjklzxcvbnm123456789-'

    d.DEBUG = True
    d.TEMPLATE_DEBUG = d.DEBUG

    d.ABSOLUTE_MEDIA_URL = d.BASE_URL + d.MEDIA_URL

    try:
        locale.setlocale(locale.LC_ALL, d.LOCALE)
    except locale.Error:
        pass

class DEFAULTS(object):
    def __init__(self, dct):
        self.__dict__['d'] = dct
    def __setattr__(self, name, value):
        if name in self.d: return
        self.d[name] = value
    def __getattr__(self, name):
        return self.d[name]

# vim: et:sta:bs=2:sw=4:
