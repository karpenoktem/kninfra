import mimetypes
import os.path
import os

from django.core.servers.basehttp import FileWrapper
from django.utils.translation import ugettext as _
from django.http import Http404, HttpResponse

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
    return HttpResponse(FileWrapper(open(p)),
            content_type=mimetypes.guess_type(p)[0])

# vim: et:sta:bs=2:sw=4:
