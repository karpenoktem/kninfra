from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from kn.planning import views

urlpatterns = [
    url(r'^$', views.planning_view, name='planning-home'),
    url(_(r'^!api/?$'), views.planning_api),
    url(_(r'^manage/$'), views.planning_poollist, name='planning-poollist'),
    url(_(r'^manage/event/new/$'), views.event_create,
        name='planning-event-create'),
    url(_(r'^manage/event/(?P<eventid>[^/]+)/$'), views.event_edit,
        name='planning-event-edit'),
    url(_(r'^manage/(?P<poolname>[^/]+)/$'), views.planning_manage,
        name='planning_manage'),
    url(_(r'^manage/(?P<poolname>[^/]+)/template/?$'), views.planning_template,
        name='planning_template'),
    ]

# vim: et:sta:bs=2:sw=4:
