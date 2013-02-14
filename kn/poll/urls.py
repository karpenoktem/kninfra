from django.conf.urls.defaults import *

from kn.poll import views

urlpatterns = patterns('',
    url(r'^vote/(?P<name>[^/]+)/$',
        views.vote, name='poll'),
)

# vim: et:sta:bs=2:sw=4:
