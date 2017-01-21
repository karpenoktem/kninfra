from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from kn.agenda import views

urlpatterns = [
    url(_(r'^agenda/?$'), views.agenda, name='agenda'),
    url(_(r'^agenda/zeus/?$'), views.agenda_zeus, name='agenda-zeus'),
    url(_(r'^ledenmail-template/?$'), views.ledenmail_template,
        name='ledenmail-template'),
    ]

# vim: et:sta:bs=2:sw=4:
