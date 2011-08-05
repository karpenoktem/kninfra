from django.conf.urls.defaults import *

import django.views.generic.simple
import django.views.generic as generic
from django.contrib.auth.decorators import login_required

from kn.leden import views

urlpatterns = patterns('',
	url(r'^$',
	login_required(generic.simple.direct_to_template),
	   {'template': 'leden/home.html'}, name='smoelen-home'),
	url(r'^gebruikers/(?:p/(?P<page>[0-9]+)/)?$',
	    views.user_list, name='user-list'),
	url(r'^naamdrager/(?P<name>[^/]+)/$',
	    views.entity_detail, name='entity-by-name'),
	url(r'^id/(?P<_id>[^/]+)/$',
	    views.entity_detail, name='entity-by-id'),
	url(r'^gebruiker/(?P<name>[^/]+)/$',
	    views.entity_detail, {'type': 'user'}, name='user-by-name'),
	url(r'^gebruiker/id/(?P<_id>[^/]+)/$',
	    views.entity_detail, {'type': 'user'}, name='user-by-id'),
	url(r'^groep/(?P<name>[^/]+)/$',
	    views.entity_detail, {'type': 'group'}, name='group-by-name'),
	url(r'^groep/id/(?P<_id>[^/]+)/$',
	    views.entity_detail, {'type': 'group'}, name='group-by-id'),
	url(r'^sofa/(?P<name>[^/]+)/$',
	    views.entity_detail, {'type': 'sofa'}, name='sofa-by-name'),
	url(r'^sofa/id/(?P<_id>[^/]+)/$',
	    views.entity_detail, {'type': 'sofa'}, name='sofa-by-id'),
	url(r'^brand/(?P<name>[^/]+)/$',
	    views.entity_detail, {'type': 'brand'}, name='brand-by-name'),
	url(r'^brand/id/(?P<_id>[^/]+)/$',
	    views.entity_detail, {'type': 'brand'}, name='brand-by-id'),
	url(r'^stempel/(?P<name>[^/]+)/$',
	    views.entity_detail, {'type': 'tag'}, name='tag-by-name'),
	url(r'^stempel/id/(?P<_id>[^/]+)/$',
	    views.entity_detail, {'type': 'tag'}, name='tag-by-id'),
	url(r'^studie/(?P<name>[^/]+)/$',
	    views.entity_detail, {'type': 'tag'}, name='study-by-name'),
	url(r'^studie/id/(?P<_id>[^/]+)/$',
	    views.entity_detail, {'type': 'study'}, name='study-by-id'),
	url(r'^instituut/(?P<name>[^/]+)/$',
	    views.entity_detail, {'type': 'institute'},
	    name='institute-by-name'),
	url(r'^instituut/id/(?P<_id>[^/]+)/$',
	    views.entity_detail, {'type': 'institute'},
	    name='institute-by-id'),
	url(r'^smoel/(?P<name>[^.]+).jpg$',
	    views.user_smoel, name='user-smoel'),
	url(r'^ik/wachtwoord$', views.ik_chpasswd, name="chpasswd"),
)

