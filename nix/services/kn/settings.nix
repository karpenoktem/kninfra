{ config, lib, pkgs, ... }:

let
  settingsFormat = pkgs.formats.json { };
  settingsFile = settingsFormat.generate "kn.settings.json" config.kn.settings;
  cfg = config.kn.settings;

in {
  options.kn.settings =
    lib.mkOption { type = lib.types.lazyAttrsOf settingsFormat.type; };

  options.kn.settingsFile = lib.mkOption {
    type = lib.types.path;
    default = settingsFile;
  };

  config.kn.settings = lib.mapAttrs (name: lib.mkDefault) (with cfg; {
    DOMAINNAME = "karpenoktem.nl";

    ALLOWED_HOSTS = [ DOMAINNAME ];

    INFRA_REPO = pkgs.kninfra;

    MEDIA_URL = "/djmedia/";
    STORAGE_URL = "/djmedia/storage";

    SCHEME = "https";

    MEDIA_ROOT = INFRA_REPO + "/media/";

    STORAGE_ROOT = "/var/lib/kndjango/storage";

    # TODO: Import sankhara:/home/infra/google-oauth-key.json into age-nix
    GOOGLE_OAUTH2_KEY = pkgs.emptyFile;

    BASE_URL = SCHEME + "://" + DOMAINNAME;
    PHOTOS_CACHE_DIR = "/var/cache/fotos";
    MAILDOMAIN = DOMAINNAME;

    LISTS_MAILDOMAIN = "lists." + DOMAINNAME;
    MAILMAN_PATH = "/var/lib/mailman";
    MAILMAN_DEFAULT_OWNER = "wortel@" + MAILDOMAIN;
    DEFAULT_FROM_EMAIL =
      "Karpe Noktems ledenadministratie <root@${MAILDOMAIN}>";

    MONGO_HOST = "localhost";
    MONGO_DB = "kn";

    MODED_MAILINGLISTS = [ "discussie" "in" "uit" "test" ];
    MOD_UI_URI = "/mailman/admindb/%s";
    MOD_DESIRED_URI_PREFIX = SCHEME + "://" + DOMAINNAME;

    MEDIAWIKI_PATH = "/srv/" + DOMAINNAME + "/htdocs/mediawiki";
    MEDIAWIKI_USER = "www-data";

    ADMINS = [
      [ "Bas Westerbaan" "bas@karpenoktem.nl" ]
      [ "Jille Timmermans" "jille@karpenoktem.nl" ]
      [ "Bram Westerbaan" "bramw@karpenoktem.nl" ]
    ];

    DAAN_SOCKET = config.kn.daan.socket;
    GIEDO_SOCKET = config.kn.giedo.socket;
    HANS_SOCKET = config.kn.hans.socket;

    GOOGLE_CALENDAR_IDS = {
      kn = "vssp95jliss0lpr768ec9spbd8@group.calendar.google.com";
      zeus = "a9jl7tuhqg7oe8stapcu9uhvk8@group.calendar.google.com";
    };

    POSTFIX_VIRTUAL_MAP = "/etc/postfix/virtual/kninfra_maps";
    POSTFIX_SLM_MAP = "/etc/postfix/virtual/kninfra_slm_maps";

    PHOTOS_DIR = "/var/fotos";

    LOCALE = "nl_NL.UTF-8";
    LANGUAGE_CODE = "nl";
    LOCALE_PATHS = [ (INFRA_REPO + "/locale") ];

    DATABASES.default = { };
    CACHE_BACKEND = "locmem:///";
    MANAGERS = ADMINS;
    TIME_ZONE = "Europe/Amsterdam";
    SITE_ID = 1;
    USE_I18N = true;

    ROOT_URLCONF = "kn.urls";

    MIDDLEWARE_CLASSES = [
      "django.contrib.sessions.middleware.SessionMiddleware"
      # "django.middleware.locale.LocaleMiddleware"
      "kn.base.backports.BackportedLocaleMiddleware"
      "django.middleware.common.CommonMiddleware"
      "django.middleware.csrf.CsrfViewMiddleware"
      "django.contrib.auth.middleware.AuthenticationMiddleware"
      "django.contrib.messages.middleware.MessageMiddleware"
      "kn.leden.giedo.SyncStatusMiddleware"
    ];

    INSTALLED_APPS = [
      "django.contrib.auth"
      "django.contrib.contenttypes"
      "django.contrib.sessions"
      "django.contrib.messages"
      "kn.leden"
      "kn.subscriptions"
      "kn.browser"
      "kn.base"
      "kn.planning"
      "kn.fotos"
      "kn.static"
      "kn.agenda"
    ];

    TEMPLATES = [{
      BACKEND = "django.template.backends.django.DjangoTemplates";
      APP_DIRS = true;
      OPTIONS.context_processors = [
        "django.contrib.auth.context_processors.auth"
        "django.template.context_processors.debug"
        "django.template.context_processors.i18n"
        "django.template.context_processors.media"
        "django.contrib.messages.context_processors.messages"
        "kn.base.context_processors.base_url"
        "kn.base.context_processors.dev_banner"
        "kn.leden.context_processors.may_manage_planning"
        "django.template.context_processors.request"
      ];
    }];

    AUTHENTICATION_BACKENDS = [ "kn.leden.auth.MongoBackend" ];
    SESSION_ENGINE = "kn.leden.sessions";
    LOGIN_REDIRECT_URL = "/smoelen/";
    DEFAULT_FILE_STORAGE = "kn.base.storage.OurFileSystemStorage";

    FORCE_SCRIPT_NAME = "";

    SMOELEN_PHOTOS_PATH = "smoelen";
    SMOELEN_WIDTH = 300;
    SMOELEN_HEIGHT = 300;

    GRAPHS_PATH = "graphs";

    EXTERNAL_URLS = {
      stukken = BASE_URL + "/groups/leden/";
      wiki = "/wiki";
      wiki-home = "/wiki/Hoofdpagina";
    };

    HOME_SLIDESHOW = map (file: MEDIA_URL + file) [
      "static/slideshow/picknicktafel.jpg"
      "static/slideshow/galapoker.jpg"
      "static/slideshow/alternatief.jpg"
      "static/slideshow/tie-dye.jpg"
      "static/slideshow/roel.jpg"
      "static/slideshow/galalampjes.jpg"
      "static/slideshow/lan.jpg"
    ];

    USERNAME_CHARS = "qwertyuiopasdfghjklzxcvbnm123456789-";

    DEBUG = true;

    MAIL_DEBUG = DEBUG;

    ABSOLUTE_MEDIA_URL = BASE_URL + MEDIA_URL;

    # http://daniel.hepper.net/blog/2014/04/fixing-1_6-w001-when-upgrading;
    TEST_RUNNER = "django.test.runner.DiscoverRunner";

    FIN_YAML_PATH = "/groups/boekenlezers/fins.yaml";

    BANK_ACCOUNT_NUMBER = "NL81 RABO 0145 9278 22";
    BANK_ACCOUNT_HOLDER = "A.S.V. Karpe Noktem";

    QUAESTOR_USERNAME = "penningmeester";

    PRIVATE_GROUPS = [ ];
  });
}
