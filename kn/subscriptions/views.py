
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils import six
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

import kn.leden.entities as Es
import kn.subscriptions.entities as subscr_Es
import kn.utils.markdown
from kn.base.http import JsonHttpResponse
from kn.base.mail import render_then_email
from kn.leden.date import date_to_dt
from kn.leden.mongo import _id
from kn.subscriptions.forms import get_add_event_form


@login_required
def event_list(request):
    open_events, closed_events, open_leden_events, \
        closed_leden_events = [], [], [], []
    for e in reversed(tuple(subscr_Es.all_events())):
        if e.is_open:
            if e.is_official:
                open_events.append(e)
            else:
                open_leden_events.append(e)
        else:
            if e.is_official:
                closed_events.append(e)
            else:
                closed_leden_events.append(e)
    return render(request, 'subscriptions/event_list.html',
                  {'open_events': open_events,
                   'closed_events': closed_events,
                   'open_leden_events': open_leden_events,
                   'closed_leden_events': closed_leden_events})


@login_required
def event_detail(request, name):
    # First, find the event.
    event = subscr_Es.event_by_name(name)
    if event is None:
        raise Http404
    # Has the user already subscribed?
    subscription = event.get_subscription(request.user)
    # What are our permissions?
    has_read_access = event.has_read_access(request.user)
    has_write_access = event.has_write_access(request.user)
    if request.method == 'POST' and 'subscribe' in request.POST:
        if not event.can_subscribe:
            raise PermissionDenied
        if subscription is not None and subscription.subscribed:
            messages.error(request, _("Je bent al aangemeld"))
        else:
            notes = request.POST['notes']
            subscription = event.subscribe(request.user, notes)
        return HttpResponseRedirect(reverse('event-detail',
                                            args=(event.name,)))
    elif request.method == 'POST' and 'unsubscribe' in request.POST:
        if not event.can_unsubscribe:
            raise PermissionDenied
        if not subscription.subscribed:
            messages.error(request, _("Je bent al afgemeld"))
        else:
            notes = request.POST['notes']
            subscription = event.unsubscribe(request.user, notes)
        return HttpResponseRedirect(reverse('event-detail',
                                            args=(event.name,)))
    elif request.method == 'POST' and 'invite' in request.POST:
        if not event.is_open:
            raise PermissionDenied
        # Find the other user
        user = Es.by_id(request.POST['who'])
        if not user or not user.is_user:
            raise Http404
        # Is the other already subscribed?
        if event.get_subscription(user) is not None:
            messages.error(request, _("%s is al aangemeld") % user.full_name)
        else:
            notes = request.POST['notes']
            event.invite(user, notes, request.user)
        return HttpResponseRedirect(reverse('event-detail',
                                            args=(event.name,)))

    users = list(filter(
        lambda u: event.get_subscription(u) is None and u != request.user,
        Es.by_name('leden').get_members()
    ))
    users.sort(key=lambda u: six.text_type(u.humanName))
    listSubscribed = sorted(event.listSubscribed, key=lambda s: s.date)
    listUnsubscribed = sorted(event.listUnsubscribed, key=lambda s: s.date)
    listInvited = sorted(event.listInvited, key=lambda s: s.date)

    ctx = {'object': event,
           'user': request.user,
           'users': users,
           'subscription': subscription,
           'listSubscribed': listSubscribed,
           'listUnsubscribed': listUnsubscribed,
           'listInvited': listInvited,
           'has_read_access': has_read_access,
           'has_write_access': has_write_access}
    return render(request, 'subscriptions/event_detail.html', ctx)


def _api_event_set_opened(request):
    if ('id' not in request.POST
            or not isinstance(request.POST['id'], six.string_types)):
        return JsonHttpResponse({'error': 'invalid or missing argument "id"'})
    e = subscr_Es.event_by_id(request.POST['id'])
    if not e:
        raise Http404
    if not e.has_write_access(request.user):
        raise PermissionDenied

    opened = {'true': True, 'false': False}.get(request.POST.get('opened'))
    if opened is True:
        e.open(request.user)
    elif opened is False:
        e.close(request.user)
    else:
        return JsonHttpResponse({
            'error': 'invalid or missing argument "opened"'
        })

    return JsonHttpResponse({'success': True})

@require_POST
@login_required
def api(request):
    action = request.POST.get('action')
    if action == 'event-set-opened':
        return _api_event_set_opened(request)
    else:
        return JsonHttpResponse({'error': 'unknown action'})


@login_required
def event_new_or_edit(request, edit=None):
    superuser = subscr_Es.is_superuser(request.user)
    if edit is not None:
        e = subscr_Es.event_by_name(edit)
        if e is None:
            raise Http404
        if not superuser and not request.user.is_related_with(e.owner) and \
                not _id(e.owner) == request.user._id:
            raise PermissionDenied
    AddEventForm = get_add_event_form(request.user, superuser, bool(edit))
    if request.method == 'POST':
        form = AddEventForm(request.POST)
        if form.is_valid():
            fd = form.cleaned_data
            # The superuser may do everything, and when you yourself are the
            # owner that's always okay too.
            if not superuser and fd['owner'] != request.user.id:
                # Check some more constraints.
                owner = Es.by_id(fd['owner'])
                if not request.user.is_related_with(owner):
                    raise PermissionDenied(
                        _('Gebruiker niet verwant met eigenaar')
                    )
                if not subscr_Es.may_set_owner(request.user, owner):
                    raise PermissionDenied(_('Mag deze eigenaar niet kiezen'))
            d = {
                'date': date_to_dt(fd['date']),
                'owner': _id(fd['owner']),
                'description': fd['description'],
                'description_html': kn.utils.markdown.parser.convert(
                    fd['description']),
                'has_public_subscriptions': fd['has_public_subscriptions'],
                'may_unsubscribe': fd['may_unsubscribe'],
                'humanName': fd['humanName'],
                'createdBy': request.user._id,
                'cost': str(fd['cost']),
                'max_subscriptions': fd['max_subscriptions'],
                'is_official': superuser}
            if edit is None:
                name = fd['name']
                # If not secretariaat, then prefix name with the username
                if fd['owner'] == request.user.id:
                    prefix = str(request.user.name) + '-'
                else:
                    prefix = str(Es.by_id(fd['owner']).name) + '-'
                if (not superuser and not name.startswith(prefix) and (
                        edit is None or e.name != name)):
                    name = prefix + name
                d['name'] = name
                d['is_open'] = True  # default for new events
                e = subscr_Es.Event(d)
            else:
                e.update(d, request.user, save=False)
            e.save()
            render_then_email(
                'subscriptions/' +
                ('event-edited' if edit else 'new-event') + '.mail.html',
                Es.by_name('secretariaat').canonical_full_email, {
                    'event': e,
                    'user': request.user
                },
                headers={
                    'In-Reply-To': e.messageId,
                    'References': e.messageId,
                },
            )
            return HttpResponseRedirect(
                reverse('event-detail', args=(e.name,)))
    elif edit is None:
        form = AddEventForm()
    else:
        d = e._data
        form = AddEventForm(d)
    ctx = {'form': form,
           'edit': edit}
    return render(request, 'subscriptions/event_new_or_edit.html', ctx)

# vim: et:sta:bs=2:sw=4:
