from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

from kn.fotos import api, views

urlpatterns = [
    # backwards compatibility with knfotos
    url(r'^fotos/view\.php$', views.compat_view, name='foto-comp-1'),
    url(r'^fotos/foto\.php$', views.compat_foto, name='foto-comp-2'),
    url(r'^fotos/index\.php$', RedirectView.as_view(
        url=reverse_lazy('fotos', kwargs={'path': ''}),
        query_string=True, permanent=True), name='foto-comp-3'),

    # TODO add fallback for old foto links
    # TODO change wiki links, etc.
    url(_(r'^foto/admin/create/?$'),
        views.fotoadmin_create_event, name='fotoadmin-create-event'),
    url(_(r'^fotos/api/?$'),
        api.view, name='fotos-api'),
    url(_(r'^fotos/(?P<path>.*)$'),
        views.fotos, name='fotos'),
    # NOTE keep up to date with media/fotos.js
    url(_(r'^foto/(?P<cache>[^/]+)/(?P<path>.*)$'),
        views.cache, name='fotos-cache'),
]

# vim: et:sta:bs=2:sw=4:
