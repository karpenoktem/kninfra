import os.path

from django.conf.urls.defaults import *
from django.conf import settings
import django.views.generic as generic
import django.views.generic.simple
from kn.base.views import direct_to_folder

from kn.static import views

urlpatterns = patterns('',
    url(r'^home/?$', views.home, name='home'),
    url(r'^default/?$', views.home),
    url(r'^/?$', views.home),
    # TODO we have to specify a separate url entry to make the reverse URL work
    #      for pages with several names.  Is there a way to do this without
    #      the duplication.
    url(r'^over/?$',
        generic.simple.direct_to_template,
            {'template': 'static/over.html'}, name='over'),
    url(r'^watis/?$',  # alias van over
        generic.simple.direct_to_template,
            {'template': 'static/over.html'}),

    url(r'^contact/?$', generic.simple.direct_to_template,
            {'template': 'static/contact.html'}, name='contact'),
    url(r'^lidworden/?$', generic.simple.direct_to_template,
            {'template': 'static/lidworden.html'}, name='lidworden'),
    url(r'^geschiedenis/?$', generic.simple.direct_to_template,
            {'template': 'static/geschiedenis.html'}, name='geschiedenis'),
    url(r'^activiteiten/?$', generic.simple.direct_to_template,
            {'template': 'static/activiteiten.html'}, name='activiteiten'),

    url(r'^akta/?$', generic.simple.direct_to_template,
            {'template': 'static/aktanokturna.html'}, name='aktanokturna'),
    url(r'^(?:an|aktanokturna)/?$', generic.simple.direct_to_template,
            {'template': 'static/aktanokturna.html'}),

    url(r'^zusjes/?$', generic.simple.direct_to_template,
            {'template': 'static/zusjes.html'}, name='zusjes'),
    url(r'^route/?$', generic.simple.direct_to_template,
            {'template': 'static/route.html'}, name='route'),
    url(r'^merchandise/?$', generic.simple.direct_to_template,
            {'template': 'static/merchandise.html'}, name='merchandise'),
    url(r'^sponsoren/?$', generic.simple.direct_to_template,
            {'template': 'static/sponsoren.html'}, name='sponsoren'),
    url(r'^media/?$', generic.simple.direct_to_template,
            {'template': 'static/media.html'}, name='media'),
    url(r'^links/?$', generic.simple.direct_to_template,
            {'template': 'static/links.html'}, name='links'),
    url(r'^robots.txt/?$', generic.simple.direct_to_template,
            {'template': 'static/robots.txt',
             'mimetype': 'text/plain'}),

    url(r'^bestuur4/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur4.html'}, name='bestuur4'),
    url(r'^bestuur5/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur5.html'}, name='bestuur5'),
    url(r'^bestuur6/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur6.html'}, name='bestuur6'),
    url(r'^bestuur7/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur7.html'}, name='bestuur7'),
    url(r'^bestuur8/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur8.html'}, name='bestuur8'),
    url(r'^bestuur9/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur9.html'}, name='bestuur9'),
    url(r'^bestuur10/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur10.html'}, name='bestuur10'),
    url(r'^bestuur11/?$', generic.simple.direct_to_template,
            {'template': 'static/bestuur11.html'}, name='bestuur11'),
    # TODO we want to use reverse, but it is not initialized properly
    #      at this moment in the request handler.
    url(r'^bestuur/?$', generic.simple.redirect_to,
            {'url': '/bestuur11'}, name='bestuur'),

    url(r'^introPoster2014/?$', generic.simple.direct_to_template,
            {'template': 'static/introPoster2014.html'},
            name='introPoster2014'),
    url(r'^introPoster2013/?$', generic.simple.direct_to_template,
            {'template': 'static/introPoster2013.html'},
            name='introPoster2013'),
    url(r'^introPoster2012/?$', generic.simple.direct_to_template,
            {'template': 'static/introPoster2012.html'},
            name='introPoster2012'),
    url(r'^introPoster2011/?$', generic.simple.direct_to_template,
            {'template': 'static/introPoster2011.html'},
            name='introPoster2011'),
    url(r'^introPoster2010/?$', generic.simple.direct_to_template,
            {'template': 'static/introPoster2010.html'},
            name='introPoster2010'),
    url(r'^introPoster2009/?$', generic.simple.direct_to_template,
            {'template': 'static/introPoster2009.html'},
            name='introPoster2009'),
    url(r'^lustrumPoster5/?$', generic.simple.direct_to_template,
            {'template': 'static/lustrumPoster5.html'},
            name='lustrumPoster5'),
    url(r'^lustrumPoster(?:10)?/?$', generic.simple.direct_to_template,
            {'template': 'static/lustrumPoster10.html'},
            name='lustrumPoster10'),
    url(r'^openweekPoster2013/?$', generic.simple.direct_to_template,
            {'template': 'static/openweekPoster2013.html'},
            name='openweekPoster2013'),

    url(r'^lustrum/?$', generic.simple.direct_to_template,
            {'template': 'static/lustrum.html'},
            name='lustrum'),
    url(r'^intro2008/?$', generic.simple.direct_to_template,
            {'template': 'static/intro2008.html'},
            name='intro2008'),
    url(r'^intro2009/?$', generic.simple.direct_to_template,
            {'template': 'static/intro2009.html'},
            name='intro2009'),
    url(r'^intro2010/?$', generic.simple.direct_to_template,
            {'template': 'static/intro2010.html'},
            name='intro2010'),

    # legacy redirect URLs
    url(r'^hink-stap/(?P<name>fotos-pdn|fotos|wiki|forum|stukken)$',
            views.hink_stap),

    # Backwards compatibility
    url(r'^img/(?P<subdir>.*)', direct_to_folder,
            {'root': os.path.join(settings.MEDIA_ROOT, 'static/img') }),
    url(r'^baragenda/?$', generic.simple.redirect_to,
            {'url': '/planning'}),  # TODO use reverse_url

    # style
    url(r'^styles/static/$',
        generic.simple.direct_to_template,
        {'template':'static/base.css',
         'mimetype':'text/css'}, name='static-base'),
)

# vim: et:sta:bs=2:sw=4:
