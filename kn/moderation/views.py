import os
import sys
import os.path
import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponse, Http404, HttpResponseRedirect

from kn.base.runtime import setup_virtual_package
from kn.leden.models import OldKnGroup

from kn.moderation.models import ModerationRecord

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

def _deactivate_mm(ml, name, user, record, moderators):
	if not ml.emergency:
		return
	ml.emergency = False
	ml.Save()
	if not record is None:
		record.delete()
	if user is None:
		EmailMessage(
			"Moderatiemodus op %s is verlopen" % name,
			("De moderatiemodus op %s is verlopen.") % name,
			'<wortel@karpenoktem.nl>',
			[moderators.primary_email]).send()
	else:
		EmailMessage(
			"Moderatiemodus op %s is uitgezet door %s" % (name,
								user.username),
			("De moderatiemodus op %s is uitgezet door %s.") % (
				name, user.username),
			'<wortel@karpenoktem.nl>',
			[moderators.primary_email]).send()

def _renew_mm(ml, name, user, record, moderators):
	if not ml.emergency:
		return
	now = datetime.datetime.now()
	until = now + settings.MOD_RENEW_INTERVAL
	if record is None:
		record = ModerationRecord(list=name)
	record.by = user
	record.at = now
	record.save()
	EmailMessage(
		"Moderatiemodus op %s is verlengd door %s" % (name,
							user.username),
		("De moderatiemodus op %s is verlengd door %s.  Deze loopt, "+
		 "indien niet verder verlengd, af om %s.") % (
			name, user.username, until.time()),
		'<wortel@karpenoktem.nl>',
		[moderators.primary_email]).send()
	return record


def _activate_mm(ml, name, user, record, moderators):
	if ml.emergency:
		return
	ml.emergency = True
	ml.Save()
	now = datetime.datetime.now()
	until = now + settings.MOD_RENEW_INTERVAL
	if record is None:
		record = ModerationRecord(list=name)
	record.by = user
	record.at = now
	record.save()
	EmailMessage(
		"Moderatiemodus op %s is aangezet door %s" % (name,
							user.username),
		("%s is op moderatiemodus gezet door %s.  Deze loopt, indien "+
		 "niet verlengd, af om %s.") % (
			name, user.username, until.time()),
		'<wortel@karpenoktem.nl>',
		[moderators.primary_email]).send()
	return record

@login_required
def overview(request):
	toggle_with_name = None
	renew_with_name = None
	if (request.user.groups.filter(
			name=settings.MODERATORS_GROUP).count() != 0):
		is_moderator = True
		moderators = OldKnGroup.objects.get(
				name=settings.MODERATORS_GROUP)
		if request.method == 'POST':
			if 'toggle' in request.POST:
				toggle_with_name = request.POST['toggle']
			if 'renew' in request.POST:
				renew_with_name = request.POST['renew']
	else:
		is_moderator = False
	lists = []
	for name in settings.MODED_MAILINGLISTS:
		try:
			r = ModerationRecord.objects.get(list=name)
		except ModerationRecord.DoesNotExist:
			r = None
		ml = Mailman.MailList.MailList(name, True)
		try:
			if toggle_with_name == name:
				if  ml.emergency:
					_deactivate_mm(ml, name, request.user,
							r, moderators)
				else:
					r = _activate_mm(ml, name, request.user,
							r, moderators)
			if renew_with_name == name:
				r = _renew_mm(ml, name, request.user, r,
						moderators)
			by = None if r is None else r.by
			remaining = (None if r is None else r.at +
				settings.MOD_RENEW_INTERVAL -
				datetime.datetime.now())
			until = (None if r is None else r.at +
					settings.MOD_RENEW_INTERVAL)
			lists.append({'name': name,
				      'real_name': ml.real_name,
				      'modmode': ml.emergency,
				      'by': by,
				      'remaining': remaining,
				      'description': ml.description,
				      'queue': len(ml.GetHeldMessageIds())})
		finally:
			ml.Unlock()
	return render_to_response('moderation/overview.html',
			{'lists': lists,
			 'is_moderator': is_moderator},
			context_instance=RequestContext(request))
