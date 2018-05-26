import mimetypes
import os
import os.path
from wsgiref.util import FileWrapper

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _


def _lines_of_file_as_set(path):
    """ Opens the file at <path>; reads all lines and returns them in a set """
    ret = set()
    with open(path) as f:
        while True:
            line = f.readline()
            if not line:
                break
            ret.add(line[:-1])
    return ret


def homedir(request, root, subdir, path):
    original_root = root
    root = os.path.abspath(root)
    p1 = os.path.realpath(os.path.join(root, subdir, 'public_html', path))
    p2 = os.path.realpath(os.path.join(root, subdir,
                                       'protected_html', path))
    if (not p1[:len(root)] == root or not p2[:len(root)] == root):
        raise ValueError(_("Going outside of the root"))
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
        response = HttpResponse(FileWrapper(open(p, 'rb')),
                                content_type=mimetypes.guess_type(p)[0])
        response['Content-Length'] = os.path.getsize(p)
        response['Content-Disposition'] = 'attachment'
        return response
    lines = set()
    if os.path.isdir(p1):
        lines.update(os.listdir(p1))
    if os.path.isdir(p2):
        lines.update(os.listdir(p2))
    if os.path.isfile(os.path.join(p1, '.ignore')):
        lines -= _lines_of_file_as_set(os.path.join(p1, '.ignore'))
    if os.path.isfile(os.path.join(p2, '.ignore')):
        lines -= _lines_of_file_as_set(os.path.join(p2, '.ignore'))
    _p = os.path.join(subdir, '...', path)
    return render(request,
                  'browser/dirlist.html',
                  {'list': [(c, os.path.join(path, c),
                             os.path.isdir(os.path.join(p1, c)) or
                             os.path.isdir(os.path.join(p2, c)))
                            for c in sorted(lines)],
                   'subdir': subdir, 'root': original_root,
                   'path': _p},
                  )


# vim: et:sta:bs=2:sw=4:
