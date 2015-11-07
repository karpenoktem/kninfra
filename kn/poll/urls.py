from django.conf.urls import url

from kn.poll import views

urlpatterns = [
    url(r'^vote/(?P<name>[^/]+)/$',
        views.vote, name='poll'),
    ]

# vim: et:sta:bs=2:sw=4:
