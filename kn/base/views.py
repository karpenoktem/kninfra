import mimetypes
import os
import os.path
from wsgiref.util import FileWrapper

from django.core.exceptions import SuspiciousOperation
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.http import is_safe_url
from django.utils.translation import ugettext as _


def direct_to_folder(request, root, subdir):
    root = os.path.abspath(root)
    p = os.path.abspath(os.path.join(root, subdir))
    if not p[:len(root)] == root:
        raise ValueError(_("Dit pad ligt buiten de root"))
    if not os.path.exists(p):
        raise Http404
    if not os.path.isfile(p):
        raise ValueError(_("%s is een map --- geen bestand") % p)
    if os.stat(p).st_mode & 4 != 4:
        raise Http404
    return HttpResponse(FileWrapper(open(p, 'rb')),
                        content_type=mimetypes.guess_type(p)[0])


def langpicker(request):
    language, url = request.POST['language-url'].split(':', 2)
    if hasattr(request, 'session'):
        request.session['_language'] = language
        if (hasattr(request, 'user') and request.user.is_authenticated()
                and language != request.user.preferred_language):
            request.user.set_preferred_language(language)
    if not is_safe_url(url):
        raise SuspiciousOperation('redirect URL fails is_safe_url')
    return redirect(url)

# vim: et:sta:bs=2:sw=4:
