from django.conf.urls.defaults import *
import django.views.generic.list_detail
from django.contrib.auth.decorators import login_required

from kn.reglementen import views

urlpatterns = patterns('',
    url(r'^/?$',
        views.reglement_list, name='reglement-list'),
    url(r'^(?P<name>[^/]+)/?$',
        views.reglement_detail, name='reglement-detail'),
    url(r'^(?P<reglement_name>[^/]+)/(?P<version_name>[^/]+)/?$',
        views.version_detail, name='version-detail'),
)

# vim: et:sta:bs=2:sw=4:
