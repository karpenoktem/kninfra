from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib.auth.views import login, logout_then_login
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView

import kn.browser.views
from kn.base.backports import i18n_patterns
from kn.leden import views

urlpatterns = [
    url(r'^favicon.ico$', RedirectView.as_view(
        url=settings.MEDIA_URL + 'base/favicon.ico', permanent=True)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    url(_(r'^groups/(?P<subdir>[^/]+)/(?P<path>.*)'),
        kn.browser.views.homedir, {'root': '/mnt/phassa/groups/'},
        name='groupfolder'),
    url(_(r'^smoelen/'), include('kn.leden.urls')),
    url(_(r'^activiteit/'), include('kn.subscriptions.urls')),
    url(_(r'^reglementen/'), include('kn.reglementen.urls')),
    url(_(r'^accounts/login/$'), login, name='login'),
    url(_(r'^accounts/logout/$'), logout_then_login, name='logout'),
    url(_(r'^accounts/api/$'), views.accounts_api, name='auth-api'),
    url(_(r'^planning/'), include('kn.planning.urls')),
    url(r'', include('kn.base.urls')),
    url(r'', include('kn.agenda.urls')),
    url(r'', include('kn.static.urls')),
    url(r'', include('kn.fotos.urls')),
    prefix_default_language=False)

# vim: et:sta:bs=2:sw=4:
