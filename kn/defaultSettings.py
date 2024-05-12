# Default settings.  Change in settings.py.  See settings.example.py.
# ###################################################################

import datetime
import locale

from django.utils.translation import ugettext_lazy as _

# We want smart default. Eg: on a particular installation BASE_URL might be
# overwritten (default: karpenoktem.nl).  However, if it is, we want other
# defaults, which depend on BASE_URL, to use the overwritten BASE_URL.
# That is why defaultSettings() is executed *after* custom settings.
# To have a nice syntax, we use a small DEFAULTS helper class.


def defaultSettings(glbls):
    d = DEFAULTS(glbls)

    # Settings you must set.
    # ############################################################

    # CHUCK_NORRIS_HIS_SECRET = 'CHANGE ME'
    # SECRET_KEY = 'CHANGE ME'
    # MAILMAN_DEFAULT_PASSWORD = 'CHANGE ME'

    # You are very likely to override these
    # These should be of the form ('host', 'user', 'password', 'db')
    # ############################################################
    d.DOMAINNAME = 'karpenoktem.nl'

    # Settings you probably want to change
    # ############################################################

    d.INFRA_HOME = '/home/infra'
    d.INFRA_REPO = d.INFRA_HOME + '/repo'

    d.MEDIA_URL = '/djmedia/'
    d.STORAGE_URL = '/djmedia/storage'

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
    d.MAILMAN_DEFAULT_OWNER = 'wortel@' + d.MAILDOMAIN
    d.DEFAULT_FROM_EMAIL = (
        'Karpe Noktems ledenadministratie <root@%s>' % d.MAILDOMAIN)

    d.MONGO_HOST = 'localhost'
    d.MONGO_DB = 'kn'

    d.MODED_MAILINGLISTS = ['discussie', 'in', 'uit', 'test']
    d.MOD_UI_URI = '/mailman/admindb/%s'
    d.MOD_RENEW_INTERVAL = datetime.timedelta(0, 15 * 60)
    d.MOD_DESIRED_URI_PREFIX = d.SCHEME + '://' + d.DOMAINNAME

    d.MEDIAWIKI_PATH = '/srv/' + d.DOMAINNAME + '/htdocs/mediawiki'
    d.MEDIAWIKI_USER = 'www-data'

    d.ADMINS = (
        ('Bas Westerbaan', 'bas@karpenoktem.nl'),
        ('Jille Timmermans', 'jille@karpenoktem.nl'),
        ('Bram Westerbaan', 'bramw@karpenoktem.nl'),
    )

    d.GIEDO_SOCKET = '/var/run/infra/S-giedo'
    d.HANS_SOCKET = '/var/run/infra/S-hans'
    d.DAAN_SOCKET = '/var/run/infra/S-daan'

    d.GOOGLE_CALENDAR_IDS = {
        'kn': 'vssp95jliss0lpr768ec9spbd8@group.calendar.google.com',
        'zeus': 'a9jl7tuhqg7oe8stapcu9uhvk8@group.calendar.google.com',
    }

    d.POSTFIX_VIRTUAL_MAP = '/etc/postfix/virtual/kninfra_maps'
    d.POSTFIX_SLM_MAP = '/etc/postfix/virtual/kninfra_slm_maps'

    d.PHOTOS_DIR = '/var/fotos'

    d.INTERNAL_IPS = ['83.162.203.144']  # bas
    d.LOCALE = 'nl_NL.UTF-8'
    d.LANGUAGE_CODE = 'nl'
    d.LOCALE_PATHS = [d.INFRA_REPO + '/locale']

    d.LANGUAGES = [
        ('nl', _('Nederlands')),
        ('en', _('Engels')),
        #    ('de', _('Duits')),
        #    ('en_PI', _('Piraat')),
    ]

    # You probably won't change this
    # ############################################################

    d.DATABASES = {'default': {}}  # We do not use Django's DB abstraction
    d.CACHE_BACKEND = 'locmem:///'
    d.MANAGERS = d.ADMINS
    d.TIME_ZONE = 'Europe/Amsterdam'
    d.SITE_ID = 1
    d.USE_I18N = True

    d.ROOT_URLCONF = 'kn.urls'
    d.MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        # 'django.middleware.locale.LocaleMiddleware',
        'kn.base.backports.BackportedLocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'kn.leden.giedo.SyncStatusMiddleware',
    )
    d.INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'kn.leden',
        'kn.subscriptions',
        'kn.browser',
        'kn.base',
        'kn.planning',
        'kn.fotos',
        'kn.static',
        'kn.agenda',
    )
    d.TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': (
                    "django.contrib.auth.context_processors.auth",
                    "django.template.context_processors.debug",
                    "django.template.context_processors.i18n",
                    "django.template.context_processors.media",
                    "django.contrib.messages.context_processors.messages",
                    "kn.base.context_processors.base_url",
                    "kn.base.context_processors.dev_banner",
                    "kn.leden.context_processors.may_manage_planning",
                    "django.template.context_processors.request",
                ),
            },
        },
    ]
    d.AUTHENTICATION_BACKENDS = (
        'kn.leden.auth.MongoBackend',
    )
    d.SESSION_ENGINE = 'kn.leden.sessions'
    d.LOGIN_REDIRECT_URL = '/smoelen/'
    d.DEFAULT_FILE_STORAGE = 'kn.base.storage.OurFileSystemStorage'

    d.FORCE_SCRIPT_NAME = ''

    d.SMOELEN_PHOTOS_PATH = 'smoelen'
    d.SMOELEN_WIDTH = 300
    d.SMOELEN_HEIGHT = 300

    d.GRAPHS_PATH = 'graphs'

    d.EXTERNAL_URLS = {
        'stukken': d.BASE_URL + '/groups/leden/',
        'wiki': '/wiki',
        'wiki-home': '/wiki/Hoofdpagina',
    }

    d.HOME_SLIDESHOW = [
        d.MEDIA_URL + 'static/slideshow/main 1.size.jpg',
        d.MEDIA_URL + 'static/slideshow/main 2.size.jpg',
        d.MEDIA_URL + 'static/slideshow/main 3.size.jpg',
        d.MEDIA_URL + 'static/slideshow/main 4.size.jpg',
        d.MEDIA_URL + 'static/slideshow/main 5.size.jpg',
    ]

    d.DT_MIN = datetime.datetime(2004, 8, 31)
    d.DT_MAX = datetime.datetime(5004, 9, 1)

    d.USERNAME_CHARS = 'qwertyuiopasdfghjklzxcvbnm123456789-'

    d.DEBUG = True
    d.MAIL_DEBUG = d.DEBUG

    d.ABSOLUTE_MEDIA_URL = d.BASE_URL + d.MEDIA_URL

    # http://daniel.hepper.net/blog/2014/04/fixing-1_6-w001-when-upgrading
    d.TEST_RUNNER = 'django.test.runner.DiscoverRunner'

    d.FIN_YAML_PATH = "/groups/boekenlezers/fins.yaml"

    d.BANK_ACCOUNT_NUMBER = "NL81 RABO 0145 9278 22"
    d.BANK_ACCOUNT_HOLDER = "A.S.V. Karpe Noktem"

    d.QUAESTOR_USERNAME = "penningmeester"

    d.PRIVATE_GROUPS = []

    try:
        locale.setlocale(locale.LC_ALL, d.LOCALE)
    except locale.Error:
        pass


class DEFAULTS(object):

    def __init__(self, dct):
        self.__dict__['d'] = dct

    def __setattr__(self, name, value):
        if name in self.d:
            return
        self.d[name] = value

    def __getattr__(self, name):
        return self.d[name]

# vim: et:sta:bs=2:sw=4:
