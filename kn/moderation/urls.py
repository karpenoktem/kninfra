# vim: et:sta:bs=2:sw=4:
from django.conf.urls.defaults import *

import kn.moderation.views as views

urlpatterns = patterns('',
	url(r'^$', views.overview, name='moderation-home'),
	url(r'^(?P<name>[^/]+)/$', views.redirect, name='moderation-redirect'),
)
