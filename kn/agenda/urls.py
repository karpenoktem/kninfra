from django.conf.urls.defaults import *

from kn.agenda import views
import django.views.generic.simple
import django.views.generic as generic

urlpatterns = patterns('',
    url(r'^agenda/?$', views.agenda, name='agenda'),
    url(r'^ledenmail-template/?$', views.ledenmail_template,
                    name='ledenmail-template'),
    url(r'^styles/agenda/$',
        generic.simple.direct_to_template,
        {'template':'agenda/agenda.css',
         'mimetype':'text/css'}, name='style-agenda'),
)

# vim: et:sta:bs=2:sw=4:
