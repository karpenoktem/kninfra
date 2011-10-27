# vim: et:sta:bs=2:sw=4:
from django.core.servers.basehttp import FileWrapper
from django.http import Http404, HttpResponse
import mimetypes
import os.path
import os

def direct_to_folder(request, root, subdir):
	root = os.path.abspath(root)
	p = os.path.abspath(os.path.join(root, subdir))
	if not p[:len(root)] == root:
		raise ValueError, "Going outside of the root"
	if not os.path.exists(p):
		raise Http404
	if not os.path.isfile(p):
		raise ValueError, "%s is a directory" % p
	if os.stat(p).st_mode & 4 != 4:
		raise Http404
	return HttpResponse(FileWrapper(open(p)),
			mimetype=mimetypes.guess_type(p)[0])
