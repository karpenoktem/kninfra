from django.contrib import auth
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
import django.contrib.auth.views

from kn.leden import views
from kn.base.views import direct_to_folder

urlpatterns = patterns('',
    url(r'^groups/(?P<subdir>[^/]+)/(?P<path>.*)',
        'kn.browser.views.homedir', {'root':'/mnt/phassa/groups/'},
                name='groupfolder'),
    (r'^smoelen/', include('kn.leden.urls')),
    (r'^activiteit/', include('kn.subscriptions.urls')),
    (r'^activiteit2/', include('kn.events.urls')),
    (r'^reglementen/', include('kn.reglementen.urls')),
    (r'^poll/', include('kn.poll.urls')),
    (r'^djmedia/(?P<subdir>.*)', direct_to_folder,
        {'root': settings.MEDIA_ROOT}),
    url(r'^accounts/login/$', auth.views.login, name='login'),
    url(r'^accounts/logout/$', auth.views.logout_then_login, name='logout'),
    url(r'^accounts/rauth/$', 'kn.leden.views.rauth', name='rauth'),
    url(r'^favicon.ico$', redirect_to,
            {'url': settings.MEDIA_URL + '/base/favicon.ico'}),
    (r'^moderatie/', include('kn.moderation.urls')),
    (r'^planning/', include('kn.planning.urls')),
    (r'^barco/', include('kn.barco.urls')),
    (r'', include('kn.agenda.urls')),
    (r'', include('kn.static.urls')),
    (r'', include('kn.fotos.urls')),
)

# vim: et:sta:bs=2:sw=4:
