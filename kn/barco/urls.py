from django.conf.urls.defaults import *
from django.views.generic import RedirectView

from kn.barco import views

urlpatterns = patterns('',
    url(r'^(?P<repos>[^/]+)/enter/(?P<formname>[^/]+)/$',
        views.barco_enterform, name='barco-enterform'),

    # legacy:
    url(r'^(?P<repos>[^/]+)/barform/$', RedirectView.as_view(
                url='/barco/%(repos)s/enter/barform/')),
)

# vim: et:sta:bs=2:sw=4:
