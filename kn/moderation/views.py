from __future__ import absolute_import

import datetime

import six

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import RequestContext
from django.utils.translation import ugettext as _

import kn.leden.entities as Es
import kn.moderation.entities as mod_Es
from kn.base.mail import render_then_email
from kn.leden import giedo


@login_required
def redirect(request, name):
    # if not request.build_absolute_uri().startswith(
    #         settings.MOD_DESIRED_URI_PREFIX):
    #     return HttpResponseRedirect(settings.MOD_DESIRED_URI_PREFIX +
    #                                 request.get_full_path())
    if not request.user.is_related_with(Es.by_name(settings.MODERATORS_GROUP)):
        return HttpResponse(_("Toegang geweigerd"))
    if name not in settings.MODED_MAILINGLISTS:
        raise Http404
    cookie_name, cookie_value = giedo.maillist_get_moderator_cookie(name)
    r = HttpResponseRedirect(settings.MOD_UI_URI % name)
    r[cookie_name] = cookie_value
    return r


def _deactivate_mm(name, user, record, moderators):
    giedo.maillist_deactivate_moderation(name)
    if record:
        record.delete()
    if user:
        render_then_email('moderation/disabled-by.mail.txt',
                          moderators.canonical_full_email, {
                              'name': name,
                              'user': user})
    else:
        render_then_email('moderation/timed-out.mail.txt',
                          moderators.canonical_full_email, {
                              'name': name})


def _renew_mm(name, user, record, moderators):
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


def _activate_mm(name, user, record, moderators):
    giedo.maillist_activate_moderation(name)
    now = datetime.datetime.now()
    until = now + settings.MOD_RENEW_INTERVAL
    if record is None:
        record = mod_Es.ModerationRecord({'list': name})
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
    """ This view is used to show the overview of the lists to be moderated,
        but also to toggle moderation (via the toggle POST variable) and
        to renew moderation (via the renew POST variable). """
    toggle_with_name = None
    renew_with_name = None
    moderators = Es.by_name(settings.MODERATORS_GROUP)

    # Check for renew/toggle in POST
    if request.user.is_related_with(Es.by_name(settings.MODERATORS_GROUP)):
        is_moderator = True
        if request.method == 'POST':
            if 'toggle' in request.POST:
                toggle_with_name = request.POST['toggle']
            if 'renew' in request.POST:
                renew_with_name = request.POST['renew']
    else:
        is_moderator = False
    lists = []

    # Check current state of mailling lists
    ml_state = giedo.maillist_get_moderated_lists()

    if six.PY3:
        # hans is running Python 2, so we will get bytes() instead of str()s,
        # lets convert it to strings for Python 3.
        ml_state = {
            name.decode(): {
                key.decode(): val.decode() if isinstance(val, str) else val
                for key, val in entry.items()
            } for name, entry in ml_state.items()
        }

    for name in sorted(ml_state):
        r = mod_Es.by_name(name)
        if toggle_with_name == name:
            if ml_state[name]['modmode']:
                _deactivate_mm(name, request.user, r, moderators)
            else:
                r = _activate_mm(name, request.user, r, moderators)
            ml_state[name]['modmode'] = not ml_state[name]['modmode']
        if renew_with_name == name and ml_state[name]['modmode']:
            r = _renew_mm(name, request.user, r, moderators)
        by = None if r is None else r.by
        remaining = (
            None if r is None else
            r.at - datetime.datetime.now() + settings.MOD_RENEW_INTERVAL)
        lists.append({
            'name': name,
            'by': by,
            'remaining': remaining,
            'real_name': ml_state[name]['real_name'],
            'modmode': ml_state[name]['modmode'],
            'description': ml_state[name]['description'],
            'queue': ml_state[name]['queue']
        })
    return render(request, 'moderation/overview.html',
                  {'lists': lists,
                   'is_moderator': is_moderator})

# vim: et:sta:bs=2:sw=4:
