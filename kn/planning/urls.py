# vim: et:sta:bs=2:sw=4:
from django.conf.urls.defaults import *

# import django.views.generic.simple
# import django.views.generic as generic
# from django.contrib.auth.decorators import login_required

from kn.planning import views

urlpatterns = patterns('',
    url(r'^$', views.planning_view, name='planning-home'),
    (r'^!api/?$', views.planning_api),
    url(r'^manage/$', views.planning_poollist, name='planning-poollist'),
    url(r'^manage/event/new/$', views.event_create,
                        name='planning-event-create'),
    url(r'^manage/event/(?P<eventid>[^/]+)/$', views.event_edit,
                        name='planning-event-edit'),
    url(r'^manage/(?P<poolname>[^/]+)/$', views.planning_manage,
                        name='planning_manage'),
    url(r'^manage/(?P<poolname>[^/]+)/template/?$', views.planning_template,
                        name='planning_template'),
)
