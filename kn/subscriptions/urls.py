from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from kn.subscriptions import views

urlpatterns = [
    url(r'^/?$',
        views.event_list, name='event-list'),
    url(r'^(?P<name>[a-zA-Z0-9\-.]+)/?$',
        views.event_detail, name='event-detail'),
    url(_(r'^!api/?$'),
        views.api, name='api'),
    url(_(r'^!nieuwe/?$'),
        views.event_new_or_edit, name='event-new'),
    url(_(r'^(?P<edit>[a-zA-Z0-9\-.]+)/edit/?$'),
        views.event_new_or_edit, name='event-edit'),
    ]

# vim: et:sta:bs=2:sw=4:
