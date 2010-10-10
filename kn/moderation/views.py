import sys
import os.path

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from kn.base.runtime import setup_virtual_package

try:
	import Mailman.MailList
except ImportError:
	setup_virtual_package('Mailman', os.path.expanduser(
					'~mailman/Mailman'))
	import Mailman.MailList


def overview(request):
	lists = []
	for name in settings.MODED_MAILINGLISTS:
		ml = Mailman.MailList.MailList(name, True)
		try:
			lists.append({'name': name,
				      'real_name': ml.real_name,
				      'modmode': ml.emergency,
				      'description': ml.description,
				      'queue': len(ml.GetHeldMessageIds())})
		finally:
			ml.Unlock()
	return render_to_response('moderation/overview.html',
			{'lists': lists},
			context_instance=RequestContext(request))
