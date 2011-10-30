# vim: et:sta:bs=2:sw=4:
from django.conf.urls.defaults import *

# import django.views.generic.simple
# import django.views.generic as generic
# from django.contrib.auth.decorators import login_required

from kn.planning import views

urlpatterns = patterns('',
    (r'^$', views.planning_view),
    url(r'^manage/$', views.planning_poollist, name='planning-poollist'),
    url(r'^manage/event/new/$', views.event_create,
                        name='planning-event-create'),
    url(r'^manage/event/(?P<eventid>[^/]+)/$', views.event_edit,
                        name='planning-event-edit'),
    url(r'^manage/(?P<poolname>[^/]+)/$', views.planning_manage,
                        name='planning_manage'),
)
