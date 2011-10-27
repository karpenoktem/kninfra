from django.conf.urls.defaults import *
import django.views.generic.list_detail

from django.contrib.auth.decorators import login_required
from kn.fotos import views

urlpatterns = patterns('',
        url(r'^admin/?$',
            views.fotoadmin_move, name='fotoadmin-move'),
        url(r'^admin/create/?$',
            views.fotoadmin_create_event, name='fotoadmin-create-event'),
)

