from django.contrib import auth
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.views.generic import RedirectView

from kn.leden import views
from kn.base.backports import i18n_patterns

urlpatterns = [
    url(r'^favicon.ico$', RedirectView.as_view(
            url=settings.MEDIA_URL + 'base/favicon.ico')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    url(r'^groups/(?P<subdir>[^/]+)/(?P<path>.*)',
        'kn.browser.views.homedir', {'root':'/mnt/phassa/groups/'},
                name='groupfolder'),
    url(r'^smoelen/', include('kn.leden.urls')),
    url(r'^activiteit/', include('kn.subscriptions.urls')),
    url(r'^reglementen/', include('kn.reglementen.urls')),
    url(r'^poll/', include('kn.poll.urls')),
    url(r'^accounts/login/$', auth.views.login, name='login'),
    url(r'^accounts/logout/$', auth.views.logout_then_login, name='logout'),
    url(r'^accounts/rauth/$', 'kn.leden.views.rauth', name='rauth'),
    url(r'^accounts/api/$', 'kn.leden.views.accounts_api', name='auth-api'),
    url(r'^moderatie/', include('kn.moderation.urls')),
    url(r'^planning/', include('kn.planning.urls')),
    url(r'^barco/', include('kn.barco.urls')),
    url(r'', include('kn.agenda.urls')),
    url(r'', include('kn.static.urls')),
    url(r'', include('kn.fotos.urls')),
        prefix_default_language=False)

# vim: et:sta:bs=2:sw=4:
