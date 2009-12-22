from django.conf.urls.defaults import *
from kn.leden import views

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
	(r'^groups/(?P<subdir>[^/]+)/(?P<path>.*)',
		'kn.browser.views.homedir', {'root':'/groups/kn'}),
	(r'^smoelen/', include('kn.leden.urls')),
	(r'^activiteit/', include('kn.subscriptions.urls')),
	(r'^poll/', include('kn.poll.urls')),
	url(r'^accounts/login/$', auth.views.login, name='login'),
	url(r'^accounts/logout/$', auth.views.logout_then_login, name='logout'),
	url(r'^accounts/rauth/$', 'kn.leden.views.rauth', name='rauth'),
)
