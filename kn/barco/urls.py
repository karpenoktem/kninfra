from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from kn.barco import views

urlpatterns = [
    url(_(r'^(?P<repos>[^/]+)/enter/(?P<formname>[^/]+)/$'),
        views.barco_enterform, name='barco-enterform'),

    # legacy:
    url(r'^(?P<repos>[^/]+)/barform/$', RedirectView.as_view(
        url='/barco/%(repos)s/enter/barform/')),
]

# vim: et:sta:bs=2:sw=4:
