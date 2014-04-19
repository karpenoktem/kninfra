from django.conf.urls.defaults import *

from kn.agenda import views

urlpatterns = patterns('',
    url(r'^/?$', views.agenda, name='agenda'),
)

# vim: et:sta:bs=2:sw=4:
