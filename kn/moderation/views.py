import os
import sys
import os.path

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect

from kn.base.runtime import setup_virtual_package
from kn.leden.models import OldKnGroup

try:
	import Mailman
except ImportError:
	setup_virtual_package('Mailman', os.path.expanduser(
					'~mailman/Mailman'))
import Mailman.MailList
import Mailman.Utils
from Mailman import mm_cfg

@login_required
def redirect(request, name):
	name = str(name)
	if (request.user.groups.filter(
			name=settings.MODERATORS_GROUP).count() == 0):
		return HttpReponse("Access denied")
	if not name in settings.MODED_MAILINGLISTS:
		raise Http404
	ml = Mailman.MailList.MailList(name, True)
	try:
		if ml.mod_password is None:
			ml.mod_password = Mailman.Utils.sha_new(
					os.urandom(10)).hexdigest()
			ml.Save()
		c = ml.MakeCookie(mm_cfg.AuthListModerator)
	finally:
		ml.Unlock()
	bits = str(c).split(': ')
	r =  HttpResponseRedirect(settings.MOD_UI_URI % name)
	r[str(bits[0])] = str(bits[1])
	return r

@login_required
def overview(request):
	toggle_with_name = None
	if (request.user.groups.filter(
			name=settings.MODERATORS_GROUP).count() != 0):
		is_moderator = True
		moderators = OldKnGroup.objects.get(
				name=settings.MODERATORS_GROUP)
		if request.method == 'POST':
			toggle_with_name = request.POST['name']
	else:
		is_moderator = False
	lists = []
	for name in settings.MODED_MAILINGLISTS:
		ml = Mailman.MailList.MailList(name, True)
		try:
			if toggle_with_name == name:
				ml.emergency = not ml.emergency
				human = 'aan' if ml.emergency else 'uit'
				ml.Save()
				EmailMessage(
					"Moderatiemodus %s %s door %s" % (
						name, human,
						request.user.username),
					("De moderatiemodus van %s is door %s"+
					" veranderd naar *%s*") % (name,
						request.user.username, human),
					'<wortel@karpenoktem.nl>',
					[moderators.primary_email]).send()
			lists.append({'name': name,
				      'real_name': ml.real_name,
				      'modmode': ml.emergency,
				      'description': ml.description,
				      'queue': len(ml.GetHeldMessageIds())})
		finally:
			ml.Unlock()
	return render_to_response('moderation/overview.html',
			{'lists': lists,
			 'is_moderator': is_moderator},
			context_instance=RequestContext(request))
