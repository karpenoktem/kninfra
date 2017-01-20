""" This module contains shims to backport functionality from newer
    versions of Django. """

import re

from django.core.urlresolvers import (RegexURLResolver, get_resolver,
        get_script_prefix, is_valid_path)

from django.utils.six.moves.urllib.parse import quote
from django.utils.translation import get_language
from django.utils.cache import patch_vary_headers
from django.utils.encoding import force_bytes, iri_to_uri
from django.http import HttpResponseRedirect
from django.utils import translation
from django.utils import lru_cache
from django.conf import settings

# i18n_patterns with prefix_default_language (backport from Django 1.10)
#
#  NOTE This backport contains some customizations for kndjango, which
#       are not in Django 1.10:
#  1. The Accept-Language header is ignored if it suggests English.
#  2. URLs like /nl/... still work even though prefix_default_language
#     is set to False.
# #############################################################################


def i18n_patterns(*urls, **kwargs):
    prefix_default_language = kwargs.pop('prefix_default_language', True)
    assert not kwargs, 'Unexpected kwargs for i18n_patterns(): %s' % kwargs
    return [BackportedLocaleRegexURLResolver(list(urls),
                prefix_default_language=prefix_default_language)]


class BackportedLocaleRegexURLResolver(RegexURLResolver):
    def __init__(self, urlconf_name, default_kwargs=None, app_name=None,
        namespace=None, prefix_default_language=True):
        super(BackportedLocaleRegexURLResolver, self).__init__(
                    None, urlconf_name, default_kwargs, app_name, namespace)
        self.prefix_default_language = prefix_default_language

    @property
    def regex(self):
        language_code = get_language() or settings.LANGUAGE_CODE
        if language_code not in self._regex_dict:
            if (language_code == settings.LANGUAGE_CODE
                        and not self.prefix_default_language):
                # NOTE this is customization 2 --- see comment above.
                regex_string = '^(?:%s/)?' % language_code
                # regex_string = ''
            else:
                regex_string = '^%s/' % language_code
            self._regex_dict[language_code] = re.compile(
                regex_string,
                re.UNICODE
            )
        return self._regex_dict[language_code]


class BackportedLocaleMiddleware(object):
    response_redirect_class = HttpResponseRedirect

    def process_request(self, request):
        # NOTE this is customization 1 --- see comment above.
        if ('HTTP_ACCEPT_LANGUAGE' in request.META
                and request.META['HTTP_ACCEPT_LANGUAGE'].lower().startswith('en')):
            del(request.META['HTTP_ACCEPT_LANGUAGE'])
        urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language \
                = backported_is_language_prefix_patterns_used(urlconf)
        language = translation.get_language_from_request(
                                request, check_path=i18n_patterns_used)
        language_from_path = translation.get_language_from_path(
                                request.path_info)
        if (not language and i18n_patterns_used
                and not prefixed_default_language):
            language = settings.LANGUAGE_CODE
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = translation.get_language()
        language_from_path = translation.get_language_from_path(
                                request.path_info)
        urlconf = getattr(request, 'urlconf', settings.ROOT_URLCONF)
        i18n_patterns_used, prefixed_default_language \
                = backported_is_language_prefix_patterns_used(urlconf)

        if (response.status_code == 404 and not language_from_path
                and i18n_patterns_used):
            language_path = '/%s%s' % (language, request.path_info)
            path_valid = is_valid_path(language_path, urlconf)
            path_needs_slash = (
                not path_valid and (
                    settings.APPEND_SLASH and not language_path.endswith('/')
                    and is_valid_path('%s/' % language_path, urlconf)
                )
            )

            if path_valid or path_needs_slash:
                script_prefix = get_script_prefix()
                language_url = backported_get_full_path(request,
                        force_append_slash=path_needs_slash).replace(
                    script_prefix,
                    '%s%s/' % (script_prefix, language),
                    1
                )
                return self.response_redirect_class(language_url)

        if not (i18n_patterns_used and language_from_path):
            patch_vary_headers(response, ('Accept-Language',))
        if 'Content-Language' not in response:
            response['Content-Language'] = language
        return response


@lru_cache.lru_cache(maxsize=None)
def backported_is_language_prefix_patterns_used(urlconf):
    for url_pattern in get_resolver(urlconf).url_patterns:
        if isinstance(url_pattern,  BackportedLocaleRegexURLResolver):
            return True, url_pattern.prefix_default_language
    return False, False


def backported_escape_uri_path(path):
    return quote(force_bytes(path), safe=b"/:@&+$,-_.!~*'()")


def backported_get_full_path(self, force_append_slash=False):
    return '%s%s%s' % (
        backported_escape_uri_path(self.path),
        '/' if force_append_slash and not self.path.endswith('/') else '',
        ('?' + iri_to_uri(self.META.get('QUERY_STRING', '')))
            if self.META.get('QUERY_STRING', '') else ''
    )
