from django.conf.urls.defaults import *
import django.views.generic.list_detail

from django.contrib.auth.decorators import login_required
from kn.subscriptions import views

urlpatterns = patterns('',
	url(r'^(?P<name>[^/]+)/?$',
	    views.event_detail, name='event-detail'),
)

