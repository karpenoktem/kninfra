import os.path

from django.conf import settings
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy  # noqa: F401
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView, TemplateView

from kn.base.views import direct_to_folder
from kn.static import views

urlpatterns = [
    url(_(r'^home/?$'), views.home, name='home'),
    url(_(r'^default/?$'), views.home, name='default'),
    url(r'^/?$', views.home, name='root'),
    # url(r'^/?$', RedirectView.as_view(
    #           url=reverse_lazy('openweek2Poster2015'))),
    # TODO we have to specify a separate url entry to make the reverse URL work
    #      for pages with several names.  Is there a way to do this without
    #      the duplication.
    url(_(r'^over/?$'),
        TemplateView.as_view(template_name='static/over.html'), name='over'),
    url(_(r'^watis/?$'),  # alias van over
        TemplateView.as_view(template_name='static/over.html'), name='watis'),

    url(_(r'^contact/?$'), TemplateView.as_view(
        template_name='static/contact.html'), name='contact'),
    url(_(r'^lidworden/?$'), TemplateView.as_view(
        template_name='static/lidworden.html'), name='lidworden'),
    url(_(r'^geschiedenis/?$'), TemplateView.as_view(
        template_name='static/geschiedenis.html'), name='geschiedenis'),
    url(_(r'^activiteiten/?$'), TemplateView.as_view(
        template_name='static/activiteiten.html'), name='activiteiten'),

    url(_(r'^akta/?$'), TemplateView.as_view(
        template_name='static/aktanokturna.html'), name='aktanokturna'),
    url(_(r'^(?:an|aktanokturna)/?$'), RedirectView.as_view(
        url='/akta')),

    url(_(r'^zusjes/?$'), TemplateView.as_view(
        template_name='static/zusjes.html'), name='zusjes'),
    url(_(r'^route/?$'), TemplateView.as_view(
        template_name='static/route.html'), name='route'),
    url(_(r'^merchandise/?$'), TemplateView.as_view(
        template_name='static/merchandise.html'), name='merchandise'),
    url(_(r'^sponsoren/?$'), TemplateView.as_view(
        template_name='static/sponsoren.html'), name='sponsoren'),
    url(_(r'^media/?$'), TemplateView.as_view(
        template_name='static/media.html'), name='media'),
    url(_(r'^links/?$'), TemplateView.as_view(
        template_name='static/links.html'), name='links'),
    url(_(r'^irc/?$'), TemplateView.as_view(
        template_name='static/irc.html'), name='irc'),
    url(r'^robots.txt/?$', TemplateView.as_view(
        template_name='static/robots.txt',
        content_type='text/plain'), name='robotstxt'),

    url(_(r'^bestuur4/?$'), TemplateView.as_view(
        template_name='static/bestuur4.html'), name='bestuur4'),
    url(_(r'^bestuur5/?$'), TemplateView.as_view(
        template_name='static/bestuur5.html'), name='bestuur5'),
    url(_(r'^bestuur6/?$'), TemplateView.as_view(
        template_name='static/bestuur6.html'), name='bestuur6'),
    url(_(r'^bestuur7/?$'), TemplateView.as_view(
        template_name='static/bestuur7.html'), name='bestuur7'),
    url(_(r'^bestuur8/?$'), TemplateView.as_view(
        template_name='static/bestuur8.html'), name='bestuur8'),
    url(_(r'^bestuur9/?$'), TemplateView.as_view(
        template_name='static/bestuur9.html'), name='bestuur9'),
    url(_(r'^bestuur10/?$'), TemplateView.as_view(
        template_name='static/bestuur10.html'), name='bestuur10'),
    url(_(r'^bestuur11/?$'), TemplateView.as_view(
        template_name='static/bestuur11.html'), name='bestuur11'),
    url(_(r'^bestuur12/?$'), TemplateView.as_view(
        template_name='static/bestuur12.html'), name='bestuur12'),
    url(_(r'^bestuur13a/?$'), TemplateView.as_view(
        template_name='static/bestuur13a.html'), name='bestuur13a'),
    url(_(r'^bestuur13b/?$'), TemplateView.as_view(
        template_name='static/bestuur13b.html'), name='bestuur13b'),
    url(_(r'^bestuur13/?$'), RedirectView.as_view(
        url='/bestuur13b'), name='bestuur13'),
    url(_(r'^bestuur14/?$'), TemplateView.as_view(
        template_name='static/bestuur14.html'), name='bestuur14'),
    # TODO we want to use reverse, but it is not initialized properly
    #      at this moment in the request handler.
    url(_(r'^bestuur/?$'), RedirectView.as_view(
        url='/bestuur14', permanent=False), name='bestuur'),

    url(_(r'^introPoster2016/?$'), TemplateView.as_view(
        template_name='static/introPoster2016.html'),
        name='introPoster2016'),
    url(_(r'^introPoster2015/?$'), TemplateView.as_view(
        template_name='static/introPoster2015.html'),
        name='introPoster2015'),
    url(_(r'^introPoster2014/?$'), TemplateView.as_view(
        template_name='static/introPoster2014.html'),
        name='introPoster2014'),
    url(_(r'^introPoster2013/?$'), TemplateView.as_view(
        template_name='static/introPoster2013.html'),
        name='introPoster2013'),
    url(_(r'^introPoster2012/?$'), TemplateView.as_view(
        template_name='static/introPoster2012.html'),
        name='introPoster2012'),
    url(_(r'^introPoster2011/?$'), TemplateView.as_view(
        template_name='static/introPoster2011.html'),
        name='introPoster2011'),
    url(_(r'^introPoster2010/?$'), TemplateView.as_view(
        template_name='static/introPoster2010.html'),
        name='introPoster2010'),
    url(_(r'^introPoster2009/?$'), TemplateView.as_view(
        template_name='static/introPoster2009.html'),
        name='introPoster2009'),
    url(_(r'^lustrumPoster5/?$'), TemplateView.as_view(
        template_name='static/lustrumPoster5.html'),
        name='lustrumPoster5'),
    url(_(r'^lustrumPoster(?:10)?/?$'), TemplateView.as_view(
        template_name='static/lustrumPoster10.html'),
        name='lustrumPoster10'),
    url(_(r'^openweekPoster2013/?$'), TemplateView.as_view(
        template_name='static/openweekPoster2013.html'),
        name='openweekPoster2013'),
    url(_(r'^openweekPoster2014/?$'), TemplateView.as_view(
        template_name='static/openweekPoster2014.html'),
        name='openweekPoster2014'),
    url(_(r'^openweekPoster2015/?$'), TemplateView.as_view(
        template_name='static/openweekPoster2015.html'),
        name='openweekPoster2015'),
    url(_(r'^openweek2Poster2015/?$'), TemplateView.as_view(
        template_name='static/openweek2Poster2015.html'),
        name='openweek2Poster2015'),
    url(_(r'^openweekPoster2016/?$'), TemplateView.as_view(
        template_name='static/openweekPoster2016.html'),
        name='openweekPoster2016'),

    url(_(r'^lustrum/?$'), TemplateView.as_view(
        template_name='static/lustrum.html'),
        name='lustrum'),
    url(_(r'^intro2008/?$'), TemplateView.as_view(
        template_name='static/intro2008.html'),
        name='intro2008'),
    url(_(r'^intro2009/?$'), TemplateView.as_view(
        template_name='static/intro2009.html'),
        name='intro2009'),
    url(_(r'^intro2010/?$'), TemplateView.as_view(
        template_name='static/intro2010.html'),
        name='intro2010'),

    # legacy redirect URLs
    url(_(r'^hink-stap/(?P<name>wiki|forum|stukken)$'),
        views.hink_stap, name='hinkstap'),

    # Backwards compatibility
    url(r'^img/(?P<subdir>.*)', direct_to_folder,
        {'root': os.path.join(settings.MEDIA_ROOT, 'static/img')}),
    url(r'^baragenda/?$', RedirectView.as_view(
        url='/planning')),  # TODO use reverse_url

    # style
    url(_(r'^styles/static/$'),
        TemplateView.as_view(template_name='static/base.css',
                             content_type='text/css'), name='static-base'),
]

# vim: et:sta:bs=2:sw=4:
