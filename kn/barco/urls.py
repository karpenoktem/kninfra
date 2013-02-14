from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from kn.barco import views

urlpatterns = patterns('',
    url(r'^(?P<repos>[^/]+)/enter/(?P<formname>[^/]+)/$',
        views.barco_enterform, name='barco-enterform'),

    # legacy:
    url(r'^(?P<repos>[^/]+)/barform/$', redirect_to,
        {'url': '/barco/%(repos)s/enter/barform/'}),
)

# vim: et:sta:bs=2:sw=4:
