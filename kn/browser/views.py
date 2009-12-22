from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.conf import settings
import os.path

def homedir(request, root, subdir, path):
	root = os.path.abspath(root)
	p1 = os.path.abspath(os.path.join(root, subdir, 'public_html', path))
	p2 = os.path.abspath(os.path.join(root, subdir, 'protected_html', path))
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
	return HttpResponse(FileWrapper(open(p)))

