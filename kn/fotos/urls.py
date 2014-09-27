from django.conf.urls.defaults import *

from kn.fotos import views

urlpatterns = patterns('',
        # TODO add fallback for old foto links
        # TODO change wiki links, etc.
        url(r'^fotos/(?P<path>.*)$',
            views.browse, name='fotos-browse'),
        url(r'^foto/(?P<cache>[^/]+)/(?P<path>.*)$',
            views.cache, name='fotos-cache'),
        url(r'^fotoAdmin/?$',
            views.fotoadmin_move, name='fotoadmin-move'),
        url(r'^fotoAdmin/create/?$',
            views.fotoadmin_create_event, name='fotoadmin-create-event'),
        url(r'^fotoAdmin/status/?$',
            views.fotoadmin_status, name='fotoadmin-status'),
)

# vim: et:sta:bs=2:sw=4:
