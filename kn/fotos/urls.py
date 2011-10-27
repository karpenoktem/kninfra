# vim: et:sta:bs=2:sw=4:
from django.conf.urls.defaults import *

from kn.fotos import views

urlpatterns = patterns('',
        url(r'^admin/?$',
            views.fotoadmin_move, name='fotoadmin-move'),
        url(r'^admin/create/?$',
            views.fotoadmin_create_event, name='fotoadmin-create-event'),
)

