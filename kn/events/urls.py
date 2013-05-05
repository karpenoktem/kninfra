from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required
import django.views.generic.list_detail

from kn.events import views

urlpatterns = patterns('',
    url(r'^/?$',
        views.event_list, name='event-list'),
    url(r'^(?P<name>[a-zA-Z0-9\-.]+)/?$',
        views.event_detail, name='event-detail'),
    url(r'^!api/?$',
        views.api, name='api'),
)

# vim: et:sta:bs=2:sw=4:
