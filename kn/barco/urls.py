# vim: et:sta:bs=2:sw=4:
from django.conf.urls.defaults import *

# import django.views.generic.simple
# import django.views.generic as generic
# from django.contrib.auth.decorators import login_required

from kn.barco import views

urlpatterns = patterns('',
    url(r'^(?P<repos>[^/]+)/barform/$', views.barco_barform,
                        name='barco-barform'),
)
