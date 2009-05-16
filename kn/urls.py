from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin, auth

admin.autodiscover()

import django.contrib.auth.views

urlpatterns = patterns('',
    # Example:
    # (r'^kn/', include('kn.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
	(r'^base/', include('kn.base.urls')),
	(r'^admin/(.*)', admin.site.root),
	(r'^smoelen/', include('kn.leden.urls')),
	(r'^accounts/login/$', auth.views.login),
	(r'^accounts/logout/$', auth.views.logout_then_login),
)
