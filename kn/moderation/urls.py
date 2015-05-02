from django.conf.urls import url

import kn.moderation.views as views

urlpatterns = [
    url(r'^$', views.overview, name='moderation-home'),
    url(r'^(?P<name>[^/]+)/$', views.redirect, name='moderation-redirect'),
    ]

# vim: et:sta:bs=2:sw=4:
