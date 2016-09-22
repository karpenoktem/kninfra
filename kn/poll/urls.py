from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from kn.poll import views

urlpatterns = [
    url(_(r'^vote/(?P<name>[^/]+)/$'),
        views.vote, name='poll'),
    ]

# vim: et:sta:bs=2:sw=4:
