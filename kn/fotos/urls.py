from django.conf.urls.defaults import *
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView

from kn.fotos import views
from kn.fotos import api

urlpatterns = patterns('',
        # backwards compatibility with knfotos
        url(r'^fotos/view\.php$', views.compat_view),
        url(r'^fotos/foto\.php$', views.compat_foto),
        url(r'^fotos/index\.php$', RedirectView.as_view(
            url=reverse_lazy('fotos', kwargs={'path':''}),
            query_string=True)),

        # TODO add fallback for old foto links
        # TODO change wiki links, etc.
        url(r'^foto/admin/?$',
            views.fotoadmin_move, name='fotoadmin-move'),
        url(r'^foto/admin/create/?$',
            views.fotoadmin_create_event, name='fotoadmin-create-event'),
        url(r'^fotos/api/?$',
            api.view, name='fotos-api'),
        url(r'^fotos/(?P<path>.*)$',
            views.fotos, name='fotos'),
        # NOTE keep up to date with media/fotos.js
        url(r'^foto/(?P<cache>[^/]+)/(?P<path>.*)$',
            views.cache, name='fotos-cache'),
)

# vim: et:sta:bs=2:sw=4:
