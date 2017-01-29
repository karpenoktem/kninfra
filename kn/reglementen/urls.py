from django.conf.urls import url

from kn.reglementen import views

urlpatterns = [
    url(r'^/?$',
        views.reglement_list, name='reglement-list'),
    url(r'^(?P<name>[^/]+)/?$',
        views.reglement_detail, name='reglement-detail'),
    url(r'^(?P<reglement_name>[^/]+)/(?P<version_name>[^/]+)/?$',
        views.version_detail, name='version-detail'),
]

# vim: et:sta:bs=2:sw=4:
