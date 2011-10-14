from django.conf.urls.defaults import *

# import django.views.generic.simple
# import django.views.generic as generic
# from django.contrib.auth.decorators import login_required

from kn.planning import views

urlpatterns = patterns('',
	(r'^$', views.planning_view),
	(r'^manage/$', views.planning_poollist),
	url(r'^manage/(?P<poolname>[^/]+)/$', views.planning_manage, name='planning_manage'),
)
