from django.conf.urls.defaults import *
from kn.leden import views

from django.contrib import auth

import django.contrib.auth.views
from kn.base.views import direct_to_folder
from django.conf import settings

urlpatterns = patterns('',
	(r'^base/', include('kn.base.urls')),
	(r'^groups/(?P<subdir>[^/]+)/(?P<path>.*)',
		'kn.browser.views.homedir', {'root':'/mnt/phassa/groups/'}),
	(r'^smoelen/', include('kn.leden.urls')),
	(r'^activiteit/', include('kn.subscriptions.urls')),
	(r'^reglementen/', include('kn.reglementen.urls')),
	(r'^poll/', include('kn.poll.urls')),
	(r'^djmedia/(?P<subdir>.*)', direct_to_folder,
		{'root': settings.MEDIA_ROOT}),
	url(r'^accounts/login/$', auth.views.login, name='login'),
	url(r'^accounts/logout/$', auth.views.logout_then_login, name='logout'),
	url(r'^accounts/rauth/$', 'kn.leden.views.rauth', name='rauth'),
	(r'^moderatie/', include('kn.moderation.urls')),
	(r'^planning/', include('kn.planning.urls')),
)
