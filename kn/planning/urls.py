from django.conf.urls import url

from kn.planning import views

urlpatterns = [
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
    ]

# vim: et:sta:bs=2:sw=4:
