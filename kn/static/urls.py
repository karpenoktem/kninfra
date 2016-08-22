import os.path

from django.conf.urls import url
from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from kn.base.views import direct_to_folder
from django.core.urlresolvers import reverse_lazy

from kn.static import views

urlpatterns = [
    url(r'^home/?$', views.home, name='home'),
    url(r'^default/?$', views.home),
    url(r'^/?$', views.home),
    #url(r'^/?$', RedirectView.as_view(
    #           url=reverse_lazy('openweek2Poster2015'))),
    # TODO we have to specify a separate url entry to make the reverse URL work
    #      for pages with several names.  Is there a way to do this without
    #      the duplication.
    url(r'^over/?$',
        TemplateView.as_view(template_name='static/over.html'), name='over'),
    url(r'^watis/?$',  # alias van over
        TemplateView.as_view(template_name='static/over.html')),

    url(r'^contact/?$', TemplateView.as_view(
            template_name='static/contact.html'), name='contact'),
    url(r'^lidworden/?$', TemplateView.as_view(
            template_name='static/lidworden.html'), name='lidworden'),
    url(r'^geschiedenis/?$', TemplateView.as_view(
            template_name='static/geschiedenis.html'), name='geschiedenis'),
    url(r'^activiteiten/?$', TemplateView.as_view(
            template_name='static/activiteiten.html'), name='activiteiten'),

    url(r'^akta/?$', TemplateView.as_view(
            template_name='static/aktanokturna.html'), name='aktanokturna'),
    url(r'^(?:an|aktanokturna)/?$', TemplateView.as_view(
            template_name='static/aktanokturna.html')),

    url(r'^zusjes/?$', TemplateView.as_view(
            template_name='static/zusjes.html'), name='zusjes'),
    url(r'^route/?$', TemplateView.as_view(
            template_name='static/route.html'), name='route'),
    url(r'^merchandise/?$', TemplateView.as_view(
            template_name='static/merchandise.html'), name='merchandise'),
    url(r'^sponsoren/?$', TemplateView.as_view(
            template_name='static/sponsoren.html'), name='sponsoren'),
    url(r'^media/?$', TemplateView.as_view(
            template_name='static/media.html'), name='media'),
    url(r'^links/?$', TemplateView.as_view(
            template_name='static/links.html'), name='links'),
    url(r'^irc/?$', TemplateView.as_view(
            template_name='static/irc.html')),
    url(r'^robots.txt/?$', TemplateView.as_view(
            template_name='static/robots.txt',
            content_type='text/plain')),

    url(r'^bestuur4/?$', TemplateView.as_view(
            template_name='static/bestuur4.html'), name='bestuur4'),
    url(r'^bestuur5/?$', TemplateView.as_view(
            template_name='static/bestuur5.html'), name='bestuur5'),
    url(r'^bestuur6/?$', TemplateView.as_view(
            template_name='static/bestuur6.html'), name='bestuur6'),
    url(r'^bestuur7/?$', TemplateView.as_view(
            template_name='static/bestuur7.html'), name='bestuur7'),
    url(r'^bestuur8/?$', TemplateView.as_view(
            template_name='static/bestuur8.html'), name='bestuur8'),
    url(r'^bestuur9/?$', TemplateView.as_view(
            template_name='static/bestuur9.html'), name='bestuur9'),
    url(r'^bestuur10/?$', TemplateView.as_view(
            template_name='static/bestuur10.html'), name='bestuur10'),
    url(r'^bestuur11/?$', TemplateView.as_view(
            template_name='static/bestuur11.html'), name='bestuur11'),
    url(r'^bestuur12/?$', TemplateView.as_view(
            template_name='static/bestuur12.html'), name='bestuur12'),
    # TODO we want to use reverse, but it is not initialized properly
    #      at this moment in the request handler.
    url(r'^bestuur/?$', RedirectView.as_view(
            url='/bestuur12'), name='bestuur'),

    url(r'^introPoster2016/?$', TemplateView.as_view(
            template_name='static/introPoster2016.html'),
            name='introPoster2016'),
    url(r'^introPoster2015/?$', TemplateView.as_view(
            template_name='static/introPoster2015.html'),
            name='introPoster2015'),
    url(r'^introPoster2014/?$', TemplateView.as_view(
            template_name='static/introPoster2014.html'),
            name='introPoster2014'),
    url(r'^introPoster2013/?$', TemplateView.as_view(
            template_name='static/introPoster2013.html'),
            name='introPoster2013'),
    url(r'^introPoster2012/?$', TemplateView.as_view(
            template_name='static/introPoster2012.html'),
            name='introPoster2012'),
    url(r'^introPoster2011/?$', TemplateView.as_view(
            template_name='static/introPoster2011.html'),
            name='introPoster2011'),
    url(r'^introPoster2010/?$', TemplateView.as_view(
            template_name='static/introPoster2010.html'),
            name='introPoster2010'),
    url(r'^introPoster2009/?$', TemplateView.as_view(
            template_name='static/introPoster2009.html'),
            name='introPoster2009'),
    url(r'^lustrumPoster5/?$', TemplateView.as_view(
            template_name='static/lustrumPoster5.html'),
            name='lustrumPoster5'),
    url(r'^lustrumPoster(?:10)?/?$', TemplateView.as_view(
            template_name='static/lustrumPoster10.html'),
            name='lustrumPoster10'),
    url(r'^openweekPoster2013/?$', TemplateView.as_view(
            template_name='static/openweekPoster2013.html'),
            name='openweekPoster2013'),
    url(r'^openweekPoster2014/?$', TemplateView.as_view(
            template_name='static/openweekPoster2014.html'),
            name='openweekPoster2014'),
    url(r'^openweekPoster2015/?$', TemplateView.as_view(
            template_name='static/openweekPoster2015.html'),
            name='openweekPoster2015'),
    url(r'^openweek2Poster2015/?$', TemplateView.as_view(
            template_name='static/openweek2Poster2015.html'),
            name='openweek2Poster2015'),
    url(r'^openweekPoster2016/?$', TemplateView.as_view(
            template_name='static/openweekPoster2016.html'),
            name='openweekPoster2016'),

    url(r'^lustrum/?$', TemplateView.as_view(
            template_name='static/lustrum.html'),
            name='lustrum'),
    url(r'^intro2008/?$', TemplateView.as_view(
            template_name='static/intro2008.html'),
            name='intro2008'),
    url(r'^intro2009/?$', TemplateView.as_view(
            template_name='static/intro2009.html'),
            name='intro2009'),
    url(r'^intro2010/?$', TemplateView.as_view(
            template_name='static/intro2010.html'),
            name='intro2010'),

    # legacy redirect URLs
    url(r'^hink-stap/(?P<name>wiki|forum|stukken)$',
            views.hink_stap),

    # Backwards compatibility
    url(r'^img/(?P<subdir>.*)', direct_to_folder,
            {'root': os.path.join(settings.MEDIA_ROOT, 'static/img') }),
    url(r'^baragenda/?$', RedirectView.as_view(
                    url='/planning')),  # TODO use reverse_url

    # style
    url(r'^styles/static/$',
        TemplateView.as_view(template_name='static/base.css',
                             content_type='text/css'), name='static-base'),
        ]

# vim: et:sta:bs=2:sw=4:
