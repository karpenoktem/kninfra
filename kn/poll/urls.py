from django.conf.urls.defaults import *
from kn.leden.models import OldKnUser, OldKnGroup, OldSeat, Study
import django.views.generic.list_detail
import django.views.generic.simple
import django.views.generic.date_based

import django.views.generic as generic
from django.contrib.auth.decorators import login_required
from kn.poll import views

urlpatterns = patterns('',
	url(r'^vote/(?P<name>[^/]+)/$',
	    views.vote, name='poll-vote'),
)

