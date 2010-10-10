from django.conf.urls.defaults import *

import kn.moderation.views as views

urlpatterns = patterns('',
	url(r'^$', views.overview, name='moderation-home'),
)
