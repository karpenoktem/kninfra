from django.conf.urls.defaults import *

from kn.agenda import views

urlpatterns = patterns('',
    url(r'^agenda/?$', views.agenda, name='agenda'),
    url(r'^agenda/zeus/?$', views.agenda_zeus, name='agenda-zeus'),
    url(r'^ledenmail-template/?$', views.ledenmail_template,
                    name='ledenmail-template'),
)

# vim: et:sta:bs=2:sw=4:
