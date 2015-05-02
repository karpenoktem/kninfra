from django.conf.urls.defaults import *
from django.contrib.auth.decorators import login_required

from kn.subscriptions import views

urlpatterns = patterns('',
        url(r'^/?$',
            views.event_list, name='event-list'),
    url(r'^(?P<name>[a-zA-Z0-9\-.]+)/?$',
        views.event_detail, name='event-detail'),
    url(r'^!api/?$',
        views.api, name='api'),
    url(r'^!nieuwe/?$',
        views.event_new_or_edit, name='event-new'),
    url(r'^(?P<edit>[a-zA-Z0-9\-.]+)/edit/?$',
        views.event_new_or_edit, name='event-edit'),
)

# vim: et:sta:bs=2:sw=4:
