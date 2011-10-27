# vim: et:sta:bs=2:sw=4:
from django.shortcuts import render_to_response
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.conf import settings
import mimetypes
import os.path
import os

def homedir(request, root, subdir, path):
    original_root = root
    root = os.path.abspath(root)
    p1 = os.path.realpath(os.path.join(root, subdir, 'public_html', path))
    p2 = os.path.realpath(os.path.join(root, subdir,
        'protected_html', path))
    if (not p1[:len(root)] == root or not p2[:len(root)] == root):
        raise ValueError, "Going outside of the root"
    if os.path.exists(p1):
        p = p1
    elif os.path.exists(p2):
        if not request.user.is_authenticated():
            return HttpResponseRedirect("%s?next=%s" % (
                settings.LOGIN_URL, request.path))
        p = p2
    else:
        raise Http404
    if os.path.isfile(p):
        # world read access?
        if os.stat(p).st_mode & 4 != 4:
            raise Http404
        response = HttpResponse(FileWrapper(open(p)),
                mimetype=mimetypes.guess_type(p)[0])
        response['Content-Length'] = os.path.getsize(p)
        return response
    l = set()
    if os.path.isdir(p1):
        l.update(os.listdir(p1))
    if os.path.isdir(p2):
        l.update(os.listdir(p2))
    _p = os.path.join(root, subdir, '...', path)
    return render_to_response('browser/dirlist.html',
            {'list': [(c, os.path.join(path, c),
                   os.path.isdir(os.path.join(p1, c)) or
                   os.path.isdir(os.path.join(p2, c)))
                    for c in sorted(l)],
             'subdir': subdir, 'root': original_root,
             'path': _p},
                                context_instance=RequestContext(request))
