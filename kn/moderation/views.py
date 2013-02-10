# vim: et:sta:bs=2:sw=4:
import os
import sys
import os.path
import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponseRedirect

import kn.leden.entities as Es
import kn.moderation.entities as mod_Es
from kn.utils.mailman import import_mailman
from kn.base.mail import render_then_email
from kn import settings

import_mailman()

import Mailman.MailList
import Mailman.Utils
from Mailman import mm_cfg

@login_required
def redirect(request, name):
    if not request.build_absolute_uri().startswith(
            settings.MOD_DESIRED_URI_PREFIX):
        return HttpResponseRedirect(settings.MOD_DESIRED_URI_PREFIX +
                        request.get_full_path())
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
    if not record is None:
        record.delete()
    for id in ml.GetHeldMessageIds():
        ml.HandleRequest(id, mm_cfg.APPROVE)
    ml.Save()
    if user is None:
        render_then_email('moderation/timed-out.mail.txt',
                moderators.canonical_full_email, {
                    'name': name})
    else:
        render_then_email('moderation/disabled-by.mail.txt',
                moderators.canonical_full_email, {
                    'name': name,
                    'user': user})

def _renew_mm(ml, name, user, record, moderators):
    if not ml.emergency:
        return
    now = datetime.datetime.now()
    until = now + settings.MOD_RENEW_INTERVAL
    if record is None:
        record = mod_Es.ModerationRecord({'list': name})
    record.by = user
    record.at = now
    record.save()
    render_then_email('moderation/extended.mail.txt',
            moderators.canonical_full_email, {
                'name': name,
                'user': user,
                'until': until})
    return record

def _activate_mm(ml, name, user, record, moderators):
    if ml.emergency:
        return
    ml.emergency = True
    ml.Save()
    now = datetime.datetime.now()
    until = now + settings.MOD_RENEW_INTERVAL
    if record is None:
        record = mod_Es.ModerationRecord({'list':name})
    record.by = user
    record.at = now
    record.save()
    render_then_email('moderation/enabled.mail.txt',
            moderators.canonical_full_email, {
                'name': name,
                'user': user,
                'until': until})
    return record

@login_required
def overview(request):
    toggle_with_name = None
    renew_with_name = None
    moderators = Es.by_name(settings.MODERATORS_GROUP)
    if (request.user.is_related_with(Es.by_name(
            settings.MODERATORS_GROUP))):
        is_moderator = True
        if request.method == 'POST':
            if 'toggle' in request.POST:
                toggle_with_name = request.POST['toggle']
            if 'renew' in request.POST:
                renew_with_name = request.POST['renew']
    else:
        is_moderator = False
    lists = []
    for name in settings.MODED_MAILINGLISTS:
        r = mod_Es.by_name(name)
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
