from django.conf.urls import url

from kn.base import views

urlpatterns = [
    url(r'^langpicker$', views.langpicker, name='langpicker'),
]

# vim: et:sta:bs=2:sw=4:
