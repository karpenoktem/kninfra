# -*- coding: utf-8 -*-

import json
import logging
import mimetypes
import re
from datetime import date
from decimal import Decimal
from hashlib import sha256
from itertools import chain
from os import path

import PIL.Image

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.core.paginator import EmptyPage, Paginator
from django.core.servers.basehttp import FileWrapper
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.template.loader_tags import BlockNode
from django.utils.crypto import constant_time_compare
from django.utils.http import urlquote
from django.utils.translation import ugettext as _

import kn.leden.entities as Es
from kn.base._random import pseudo_randstr
from kn.base.conf import DT_MAX, DT_MIN
from kn.base.http import JsonHttpResponse, redirect_to_referer
from kn.base.mail import render_then_email
from kn.base.text import humanized_enum
from kn.fotos.utils import resize_proportional
from kn.leden import giedo
from kn.leden.auth import login_or_basicauth_required
from kn.leden.date import date_to_dt, now
from kn.leden.fin import BalansInfo, quaestor
from kn.leden.forms import (AddGroupForm, AddStudyForm, AddUserForm,
                            ChangePasswordForm)
from kn.leden.mongo import _id

logger = logging.getLogger(__name__)


@login_required
def user_list(request, page):
    pr = Paginator(Es.ecol.find({'types': 'user'}).sort(
        'humanNames.human', 1), 20)
    try:
        p = pr.page(1 if page is None else page)
    except EmptyPage:
        raise Http404
    return render_to_response('leden/user_list.html',
                              {'users': [Es.User(m) for m in p.object_list],
                               'page_obj': p, 'paginator': pr},
                              context_instance=RequestContext(request))


@login_required
def entity_detail(request, name=None, _id=None, type=None):
    if name is not None:
        e = Es.by_name(name)
    else:
        e = Es.by_id(_id)
    if e is None:
        raise Http404
    if type and type not in e.types:
        raise ValueError(_("Entiteit is niet een %s") % type)
    if not type:
        type = e.type
    if type not in Es.TYPE_MAP:
        raise ValueError(_("Onbekende entiteit type"))
    return globals()['_' + type + '_detail'](
        request,
        getattr(e, 'as_' + type)()
    )


def _entity_detail(request, e):
    related = sorted(e.get_related(),
                     key=lambda x: (Es.DT_MIN - Es.relation_until(x),
                                    Es.entity_humanName(x['with']),
                                    Es.entity_humanName(x['how'])))
    rrelated = sorted(e.get_rrelated(),
                      key=lambda x: (Es.DT_MIN - Es.relation_until(x),
                                     Es.entity_humanName(x['how']),
                                     Es.entity_humanName(x['who'])))
    for r in chain(related, rrelated):
        r['may_end'] = Es.user_may_end_relation(request.user, r)
        r['id'] = r['_id']
        r['until_year'] = (None if r['until'] is None
                           or r['until'] >= now()
                           else Es.date_to_year(r['until']))
        r['virtual'] = Es.relation_is_virtual(r)
    tags = [t.as_primary_type() for t in e.get_tags()]

    # mapping of year => set of members
    year_sets = {}
    for r in rrelated:
        year = r['until_year']
        if year is None:
            year = 'this'

        if year not in year_sets:
            year_sets[year] = set()
        year_sets[year].add(r['who'])

    year_counts = {}
    for year in year_sets:
        year_counts[year] = len(year_sets[year])

    ctx = {'related': related,
           'rrelated': rrelated,
           'year_counts': year_counts,
           'now': now(),
           'tags': sorted(tags, key=Es.entity_humanName),
           'object': e,
           'chiefs': [],
           'pipos': [],
           'reps': []}
    for r in rrelated:
        if r['how'] and Es.relation_is_active(r):
            if str(r['how'].name) == '!brand-hoofd':
                r['hidden'] = True
                ctx['chiefs'].append(r)
            if str(r['how'].name) == '!brand-bestuurspipo':
                r['hidden'] = True
                ctx['pipos'].append(r)
            if str(r['how'].name) == '!brand-vertegenwoordiger':
                r['hidden'] = True
                ctx['reps'].append(r)
    # Is request.user allowed to add (r)relations?
    if ('secretariaat' in request.user.cached_groups_names
            and (e.is_group or e.is_user)):
        groups = [g for g in Es.groups() if not g.is_virtual]
        groups.sort(key=Es.entity_humanName)
        users = sorted(Es.users(), key=Es.entity_humanName)
        brands = sorted(Es.brands(), key=Es.entity_humanName)
        ctx.update({'users': users,
                    'brands': brands,
                    'groups': groups,
                    'may_add_related': True,
                    'may_add_rrelated': True,
                    'may_tag': True,
                    'may_untag': True})
    ctx['may_upload_smoel'] = e.name and request.user.may_upload_smoel_for(e)
    if e.is_tag:
        ctx.update({'tag_bearers': sorted(e.as_tag().get_bearers(),
                                          key=Es.entity_humanName)})

    # Check whether entity has a photo
    photos_path = (path.join(settings.SMOELEN_PHOTOS_PATH, str(e.name))
                   if e.name else None)
    if photos_path and default_storage.exists(photos_path + '.jpg'):
        img = PIL.Image.open(default_storage.open(photos_path + '.jpg'))
        width, height = img.size
        if default_storage.exists(photos_path + '.orig'):
            # smoel was created using newer strategy. Shrink until it fits the
            # requirements.
            width, height = resize_proportional(img.size[0], img.size[1],
                                                settings.SMOELEN_WIDTH,
                                                settings.SMOELEN_HEIGHT)
        elif width > settings.SMOELEN_WIDTH:
            # smoel was created as high-resolution image, probably 600px wide
            width /= 2
            height /= 2
        else:
            # smoel was created as normal image, probably 300px wide
            pass
        ctx.update({
            'hasPhoto': True,
            'photoWidth': width,
            'photoHeight': height})
    return ctx


def _user_detail(request, user):
    ctx = _entity_detail(request, user)
    ctx['photosUrl'] = (reverse('fotos', kwargs={'path': ''})
                        + '?q=tag:' + str(user.name))
    ctx['addStudyFormOpen'] = False
    if request.method == 'POST':
        addStudyForm = AddStudyForm(request.POST)
        if 'action' in request.POST and request.POST['action'] == 'add-study':
            if 'secretariaat' not in request.user.cached_groups_names:
                raise PermissionDenied
            ctx['addStudyFormOpen'] = True
            if addStudyForm.is_valid():
                fd = addStudyForm.cleaned_data
                # TODO: catch error when study start overlaps with last study
                user.study_start(fd['study'], fd['study_inst'],
                                 fd['study_number'], fd['study_from'])
                return redirect_to_referer(request)
    else:
        addStudyForm = AddStudyForm()
    if user.last_study_end_date < DT_MAX:
        ctx['addStudyForm'] = addStudyForm
    return render_to_response('leden/user_detail.html', ctx,
                              context_instance=RequestContext(request))


def _group_detail(request, group):
    ctx = _entity_detail(request, group)
    isFreeToJoin = group.has_tag(Es.id_by_name('!free-to-join', True))
    rel_id = None
    if isFreeToJoin:
        dt = now()
        rel = list(Es.query_relations(request.user, group, None,
                                      dt, dt, False, False, False))
        assert len(rel) <= 1
        for r in rel:
            rel_id = r['_id']
    ctx.update({'isFreeToJoin': group.has_tag(Es.by_name('!free-to-join')),
                'request': request,
                'relation_with_group': rel_id})
    return render_to_response('leden/group_detail.html', ctx,
                              context_instance=RequestContext(request))


def _tag_detail(request, tag):
    ctx = _entity_detail(request, tag)
    return render_to_response('leden/tag_detail.html', ctx,
                              context_instance=RequestContext(request))


def _brand_detail(request, brand):
    ctx = _entity_detail(request, brand)
    ctx['rels'] = sorted(Es.query_relations(how=brand, deref_who=True,
                                            deref_with=True),
                         key=lambda x: (Es.DT_MIN - Es.relation_until(x),
                                        Es.entity_humanName(x['with']),
                                        Es.entity_humanName(x['who'])))
    for r in ctx['rels']:
        r['id'] = r['_id']
        r['until_year'] = (None if r['until'] is None else
                           Es.date_to_year(r['until']))
        r['virtual'] = Es.relation_is_virtual(r)
    return render_to_response('leden/brand_detail.html', ctx,
                              context_instance=RequestContext(request))


def _study_detail(request, study):
    ctx = _entity_detail(request, study)
    ctx['students'] = students = []

    for student in Es.by_study(study):
        for _study in student.studies:
            if _study['study'] != study:
                continue
            students.append({'student': student,
                             'from': _study['from'],
                             'until': _study['until'],
                             'institute': _study['institute']})
    ctx['students'].sort(key=lambda s: (Es.dt_until(s['until']),
                                        s['student'].humanName))
    return render_to_response('leden/study_detail.html', ctx,
                              context_instance=RequestContext(request))


def _institute_detail(request, institute):
    ctx = _entity_detail(request, institute)
    ctx['students'] = students = []

    for student in Es.by_institute(institute):
        for _study in student.studies:
            if _study['institute'] != institute:
                continue
            students.append({'student': student,
                             'from': _study['from'],
                             'until': _study['until'],
                             'study': _study['study']})
    ctx['students'].sort(key=lambda s: (Es.dt_until(s['until']),
                                        s['student'].humanName))
    return render_to_response('leden/institute_detail.html', ctx,
                              context_instance=RequestContext(request))


@login_required
def entities_by_year_of_birth(request, year):
    _year = int(year)
    ctx = {'year': _year,
           'users': sorted(Es.by_year_of_birth(_year),
                           key=lambda x: x.humanName)}
    years = Es.get_years_of_birth()
    if _year + 1 in years:
        ctx['next_year'] = _year + 1
    if _year - 1 in years:
        ctx['previous_year'] = _year - 1
    return render_to_response('leden/entities_by_year_of_birth.html', ctx,
                              context_instance=RequestContext(request))


@login_required
def years_of_birth(request):
    return render_to_response('leden/years_of_birth.html', {
        'years': reversed(Es.get_years_of_birth())},
        context_instance=RequestContext(request))


@login_required
def users_underage(request):
    users = sorted(Es.by_age(max_age=18), key=lambda x: x.dateOfBirth)
    users = filter(lambda u: u.is_active, users)
    final_date = None
    if users:
        youngest = users[-1]
        final_date = youngest.dateOfBirth.replace(
            year=youngest.dateOfBirth.year + 18
        )
    return render_to_response('leden/entities_underage.html', {
        'users': users,
        'final_date': final_date},
        context_instance=RequestContext(request))


@login_required
def ik(request):
    return HttpResponseRedirect(request.user.get_absolute_url())


@login_required
def ik_chsmoel(request):
    if 'smoel' not in request.FILES:
        raise ValueError(_("Missende `smoel' in FILES"))
    if 'id' not in request.POST:
        raise ValueError(_("Missende `id' in POST"))
    user = Es.by_id(request.POST['id'])
    if not user.name:
        raise ValueError(_("Entiteit heeft geen naam"))
    if not request.user.may_upload_smoel_for(request.user):
        raise PermissionDenied
    original = default_storage.open(
        path.join(settings.SMOELEN_PHOTOS_PATH,
                  str(user.name)) + ".orig", 'wb+'
    )
    for chunk in request.FILES['smoel'].chunks():
        original.write(chunk)
    original.seek(0)
    img = PIL.Image.open(original)
    if hasattr(img, '_getexif') and img._getexif() is not None:
        orientation = int(img._getexif().get(274, '1'))  # Orientation
        if orientation == 3:
            img = img.transpose(PIL.Image.ROTATE_180)
        elif orientation == 6:
            img = img.transpose(PIL.Image.ROTATE_270)
        elif orientation == 8:
            img = img.transpose(PIL.Image.ROTATE_90)
    width, height = resize_proportional(img.size[0], img.size[1],
                                        settings.SMOELEN_WIDTH * 2,
                                        settings.SMOELEN_HEIGHT * 2)
    img = img.resize((width, height), PIL.Image.ANTIALIAS)
    img.save(default_storage.open(
        path.join(settings.SMOELEN_PHOTOS_PATH,
                  str(user.name)) + ".jpg", 'w'
    ), "JPEG")
    Es.notify_informacie('set_smoel', request.user, entity=user)
    return redirect_to_referer(request)


@login_required
def user_smoel(request, name):
    user = Es.by_name(name)
    if not user:
        raise Http404
    try:
        img = default_storage.open(path.join(
            settings.SMOELEN_PHOTOS_PATH,
            str(user.name)) + ".jpg")
    except IOError:
        raise Http404
    return HttpResponse(FileWrapper(img), content_type="image/jpeg")


def _ik_chpasswd_handle_valid_form(request, form):
    oldpw = form.cleaned_data['old_password']
    newpw = form.cleaned_data['new_password']
    giedo.change_password(str(request.user.name), oldpw, newpw)
    t = _("""Lieve %s, maar natuurlijk, jouw wachtwoord is veranderd.""")
    messages.info(request, t % request.user.first_name)
    return HttpResponseRedirect(reverse('smoelen-home'))


@login_required
def ik_chpasswd(request):
    errl = []
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            try:
                return _ik_chpasswd_handle_valid_form(request,
                                                      form)
            except giedo.ChangePasswordError as e:
                errl.extend(e.args)
    else:
        form = ChangePasswordForm()
    errl.extend(form.non_field_errors())
    errstr = humanized_enum(errl)
    return render_to_response('leden/ik_chpasswd.html',
                              {'form': form, 'errors': errstr},
                              context_instance=RequestContext(request))


def rauth(request):
    """
        An implementation of Jille Timmermans' rauth scheme
        The token that is given to the authenticated user is only valid until
        the end of the day.
    """
    if request.REQUEST.get('url') is None:
        raise Http404
    if (request.REQUEST.get('validate') is not None and
            request.REQUEST.get('user') is not None):
        token = sha256('%s|%s|%s|%s' % (
            request.REQUEST['user'],
            date.today(),
            request.REQUEST['url'],
            settings.SECRET_KEY)).hexdigest()
        if constant_time_compare(request.REQUEST['validate'], token):
            return HttpResponse("OK")
        return HttpResponse("INVALID")

    '''
    The next check will allow you to request information about the user that
    is currently logged in using the 'fetch'-get attribute with the property
    names seperated by commas.
    A JSON string will be returned containing the information.
    '''
    if (request.REQUEST.get('fetch') is not None and
            request.REQUEST.get('user') is not None):
        token = sha256('%s|%s|%s|%s' % (
            request.REQUEST['user'],
            date.today(),
            request.REQUEST['url'],
            settings.SECRET_KEY)).hexdigest()
        if constant_time_compare(request.REQUEST['token'], token):
            user = Es.by_name(request.REQUEST['user'])
            properties = {
                'firstname': user.first_name,
                'lastname': user.last_name,
                'fullname': user.full_name,
                'groups': list(user.cached_groups_names)
            }
            return HttpResponse(json.dumps(dict([
                (k, properties[k]) for k in
                set(s.strip() for s in request.REQUEST.get('fetch').split(','))
                if k in properties
            ])))
        return HttpResponse("INVALID TOKEN")
    if not request.user.is_authenticated():
        return redirect_to_login('%s?url=%s' % (
            reverse('rauth'),
            urlquote(request.REQUEST['url'])))
    token = sha256('%s|%s|%s|%s' % (str(request.user.name),
                                    date.today(),
                                    request.REQUEST['url'],
                                    settings.SECRET_KEY)).hexdigest()
    return HttpResponseRedirect('%s%suser=%s&token=%s' % (
        request.REQUEST['url'],
        '?' if request.REQUEST['url'].find('?') == -1 else '&',
        str(request.user.name), token))


def accounts_api(request):
    if request.user.is_authenticated():
        ret = {'valid': True,
               'name': request.user.get_username()}
    else:
        ret = {'valid': False}

    return JsonHttpResponse(ret)


def api_users(request):
    verified_key = False
    for key in settings.ALLOWED_API_KEYS:
        if constant_time_compare(request.REQUEST['key'], key):
            verified_key = True
    if not verified_key:
        raise PermissionDenied
    ret = {}
    for m in Es.users():
        ret[str(m.name)] = m.full_name
    return HttpResponse(json.dumps(ret), content_type="text/json")


@login_required
def secr_add_user(request):
    if 'secretariaat' not in request.user.cached_groups_names:
        raise PermissionDenied
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            fd = form.cleaned_data
            # First, create the entity.
            u = Es.User({
                'types': ['user'],
                'names': [fd['username']],
                'humanNames': [{'human': fd['first_name'] + ' ' +
                                fd['last_name']}],
                'person': {
                    'titles': [],
                    'nick': fd['first_name'],
                    'given': None,
                    'family': fd['last_name'],
                    'dateOfBirth': date_to_dt(
                        fd['dateOfBirth'])
                },
                'emailAddresses': [
                    {'email': fd['email'],
                     'from': DT_MIN,
                     'until': DT_MAX}],
                'addresses': [
                    {'street': fd['addr_street'],
                     'number': fd['addr_number'],
                     'zip': fd['addr_zip'],
                     'city': fd['addr_city'],
                     'from': DT_MIN,
                     'until': DT_MAX}],
                'telephones': [
                    {'number': fd['telephone'],
                     'from': DT_MIN,
                     'until': DT_MAX}],
                'studies': [
                    {'institute': _id(fd['study_inst']),
                     'study': _id(fd['study']),
                     'from': DT_MIN,
                     'until': DT_MAX,
                     'number': fd['study_number']}],
                'is_active': True,
                'password': None
            })
            logging.info("Added user %s" % fd['username'])
            u.save()
            # Then, add the relations.
            groups = ['leden']
            if fd['incasso']:
                groups.append('incasso')
            else:
                groups.append('geen-incasso')
            for group in groups:
                Es.add_relation(u, Es.id_by_name(group,
                                                 use_cache=True),
                                _from=date_to_dt(fd['dateJoined']))
            for l in fd['addToList']:
                Es.add_relation(u, Es.id_by_name(l, use_cache=True),
                                _from=now())
            # Let giedo synch. to create the e-mail adresses, unix user, etc.
            # TODO use giedo.async() and let giedo send the welcome e-mail
            giedo.sync()
            # Create a new password and send it via e-mail
            pwd = pseudo_randstr()
            u.set_password(pwd)
            giedo.change_password(str(u.name), pwd, pwd)
            render_then_email("leden/set-password.mail.txt", u, {
                'user': u,
                'password': pwd})
            # Send the welcome e-mail
            render_then_email("leden/welcome.mail.txt", u, {
                'u': u})
            Es.notify_informacie('adduser', request.user, entity=u._id)
            return HttpResponseRedirect(reverse('user-by-name',
                                                args=(fd['username'],)))
    else:
        form = AddUserForm()
    return render_to_response('leden/secr_add_user.html',
                              {'form': form},
                              context_instance=RequestContext(request))


@login_required
def secr_notes(request):
    if 'secretariaat' not in request.user.cached_groups_names:
        raise PermissionDenied
    return render_to_response('leden/secr_notes.html',
                              {'notes': Es.get_open_notes()},
                              context_instance=RequestContext(request))


@login_required
def secr_add_group(request):
    if 'secretariaat' not in request.user.cached_groups_names:
        raise PermissionDenied
    if request.method == 'POST':
        form = AddGroupForm(request.POST)
        if form.is_valid():
            fd = form.cleaned_data
            nm = fd['name']
            g = Es.Group({
                'types': ['group', 'tag'],
                'names': [nm],
                'use_mailman_list': fd['true_group'],
                'has_unix_group': fd['true_group'],
                'humanNames': [{'name': nm,
                                'human': fd['humanName'],
                                'genitive_prefix': fd['genitive_prefix']}],
                'description': fd['description'],
                'tags': [_id(fd['parent'])]})
            logging.info("Added group %s" % nm)
            g.save()
            Es.notify_informacie('addgroup', request.user, entity=g._id)
            giedo.sync_async(request)
            messages.info(request, 'Groep toegevoegd.')
            return HttpResponseRedirect(reverse('group-by-name', args=(nm,)))
    else:
        form = AddGroupForm()
    return render_to_response('leden/secr_add_group.html', {'form': form},
                              context_instance=RequestContext(request))


@login_required
def fiscus_debtmail(request):

    if 'fiscus' not in request.user.cached_groups_names:
        raise PermissionDenied

    data = dict([(n, {'debt': Decimal(debt)}) for (n, debt) in
                 giedo.fin_get_debitors()])

    for user in Es.users():
        name = user.full_name
        if name in data:
            data[name]['user'] = user

    ctx = {
        'BASE_URL': settings.BASE_URL,
        'quaestor': quaestor(),
        'account_number': settings.BANK_ACCOUNT_NUMBER,
        'account_holder': settings.BANK_ACCOUNT_HOLDER,
    }

    if request.method == 'POST' and 'debitor' in request.POST:
        users_to_email = request.POST.getlist('debitor')
        for user_name in users_to_email:
            user = Es.by_name(user_name)

            ctx['first_name'] = user.first_name,
            ctx['debt'] = data[user.full_name]['debt']

            try:
                render_then_email("leden/debitor.mail.txt",
                                  to=user, ctx=ctx,
                                  cc=[],  # ADD penningmeester
                                  from_email=ctx['quaestor']['email'],
                                  reply_to=ctx['quaestor']['email'])
                messages.info(
                    request,
                    _("Email gestuurd naar %s.") %
                    user_name)
            except Exception as e:
                messages.error(request,
                               _("Email naar %(user)s faalde: %(e)s.") %
                               {'user': user_name, 'e': repr(e)})

    # get a sample of the email that will be sent for the quaestor's review.
    email = ""
    email_template = get_template('leden/debitor.mail.txt')

    ctx['first_name'] = '< Naam >'
    ctx['debt'] = '< Debet >'
    context = Context(ctx)
    for node in email_template:
        if isinstance(node, BlockNode) and node.name == "plain":
            email = node.render(context)
            break

    return render_to_response('leden/fiscus_debtmail.html',
                              {'data': data, 'email': email},
                              context_instance=RequestContext(request))


@login_required
def relation_end(request, _id):
    rel = Es.relation_by_id(_id)
    if rel is None:
        raise Http404
    if not Es.relation_is_active(rel):
        messages.info(request, _("Relatie was al beëindigd."))
        return redirect_to_referer(request)
    if not Es.user_may_end_relation(request.user, rel):
        raise PermissionDenied
    Es.end_relation(_id)

    # Notify informacie
    # TODO (rik) leave out 'als lid'
    Es.notify_informacie('relation_end', request.user, relation=_id)

    giedo.sync_async(request)
    return redirect_to_referer(request)


@login_required
def relation_begin(request):
    # TODO We should use Django forms, or better: use sweet Ajax
    d = {}
    for t in ('who', 'with', 'how'):
        if t not in request.POST:
            raise ValueError("Missing attr %s" % t)
        if t == 'how' and (not request.POST[t] or
                           request.POST[t] == 'null'):
            d[t] = None
        else:
            d[t] = _id(request.POST[t])
    if not Es.user_may_begin_relation(request.user, d['who'], d['with'],
                                      d['how']):
        raise PermissionDenied

    # Check whether such a relation already exists
    dt = now()
    ok = False
    try:
        next(Es.query_relations(who=d['who'], _with=d['with'],
                                how=d['how'], _from=dt, until=DT_MAX))
    except StopIteration:
        ok = True
    if not ok:
        messages.info(request, _("Deze relatie bestaat al"))
        return redirect_to_referer(request)

    # Add the relation!
    relation_id = Es.add_relation(d['who'], d['with'], d['how'], dt, DT_MAX)

    # Notify informacie
    # TODO (rik) leave out 'als lid'
    Es.notify_informacie('relation_begin', request.user, relation=relation_id)

    giedo.sync_async(request)
    return redirect_to_referer(request)


def _get_group_and_tag(request):
    '''
    Helper for tag and untag to quickly get the group and tag from a request or
    raise an error on invalid input.
    '''
    if 'group' not in request.POST:
        raise ValueError('Missing group')
    group = Es.by_id(request.POST['group'])
    if not group:
        raise Http404('group does not exist')
    if not group.is_group:
        raise ValueError(_("'group' is niet een groep"))

    if 'tag' not in request.POST:
        raise ValueError('Missing tag')
    tag = Es.by_id(request.POST['tag'])
    if not tag:
        raise Http404('tag does not exist')
    if not tag.is_tag:
        raise ValueError(_("'tag' is niet een stempel"))

    return group, tag


@login_required
def tag(request):
    group, tag = _get_group_and_tag(request)
    if not Es.user_may_tag(request.user, group, tag):
        raise PermissionDenied

    group.tag(tag)
    Es.notify_informacie('tag', request.user, entity=group, tag=tag)
    giedo.sync_async(request)
    return redirect_to_referer(request)


@login_required
def untag(request):
    group, tag = _get_group_and_tag(request)
    if not Es.user_may_untag(request.user, group, tag):
        raise PermissionDenied

    group.untag(tag)
    Es.notify_informacie('untag', request.user, entity=group, tag=tag)
    giedo.sync_async(request)
    return redirect_to_referer(request)


@login_required
def user_reset_password(request, _id):
    if 'secretariaat' not in request.user.cached_groups_names:
        raise PermissionDenied
    u = Es.by_id(_id).as_user()
    if not u.is_active:
        raise ValueError(_("Gebruiker is niet geactiveerd"))
    pwd = pseudo_randstr()
    u.set_password(pwd)
    giedo.change_password(str(u.name), pwd, pwd)
    render_then_email("leden/reset-password.mail.txt", u, {
        'user': u,
        'password': pwd})
    messages.info(request, _("Wachtwoord gereset!"))
    return redirect_to_referer(request)


@login_required
def note_add(request):
    if 'secretariaat' not in request.user.cached_groups_names:
        raise PermissionDenied
    if 'on' not in request.POST or 'note' not in request.POST:
        raise ValueError(_("missende `on' of `note'"))
    on = Es.by_id(_id(request.POST['on']))
    if on is None:
        raise Http404
    note = on.add_note(request.POST['note'], request.user)
    render_then_email("leden/new-note.mail.html",
                      Es.by_name('secretariaat').canonical_full_email, {
                          'user': request.user,
                          'note': request.POST['note'],
                          'on': on},
                      headers={
                          'In-Reply-To': note.messageId,
                          'References': note.messageId})
    return redirect_to_referer(request)


@login_required
def secr_update_site_agenda(request):
    if 'secretariaat' not in request.user.cached_groups_names:
        raise PermissionDenied
    giedo.update_site_agenda()
    messages.info(request, _("Agenda geupdate!"))
    return redirect_to_referer(request)


@login_required
def ik_openvpn(request):
    password_incorrect = False
    if 'want' in request.POST and 'password' in request.POST:
        # TODO password versions
        if request.user.check_password(request.POST['password']):
            giedo.change_password(str(request.user.name),
                                  request.POST['password'],
                                  request.POST['password'])
            giedo.openvpn_create(str(request.user.name),
                                 request.POST['want'])
            messages.info(request, _("Je verzoek wordt verwerkt. "
                                     "Verwacht binnen 5 minuten een e-mail."))
            return HttpResponseRedirect(reverse('smoelen-home'))
        else:
            password_incorrect = True
    return render_to_response('leden/ik_openvpn.html',
                              {'password_incorrect': password_incorrect},
                              context_instance=RequestContext(request))


@login_or_basicauth_required
def ik_openvpn_download(request, filename):
    m1 = re.match('^openvpn-install-([0-9a-f]+)-([^.]+)\.exe$', filename)
    m2 = re.match('^openvpn-config-([^.]+)\.zip$', filename)
    if not m1 and not m2:
        raise Http404
    if m1 and m1.group(2) != str(request.user.name):
        raise PermissionDenied
    if m2 and m2.group(1) != str(request.user.name):
        raise PermissionDenied
    p = path.join(settings.VPN_INSTALLER_PATH, filename)
    if not default_storage.exists(p):
        raise Http404
    response = HttpResponse(
        FileWrapper(default_storage.open(p)),
        content_type=mimetypes.guess_type(default_storage.path(p))[0]
    )
    response['Content-Length'] = default_storage.size(p)
    # XXX use ETags and returns 304's
    return response


@login_required
def ik_balans(request):
    balans = giedo.fin_get_account(request.user)
    return render_to_response('leden/ik_balans.html',
                              {'balans': BalansInfo(balans),
                               'quaestor': quaestor()},
                              context_instance=RequestContext(request))


def language(request):
    return HttpResponse(str(request.LANGUAGE_CODE))

# vim: et:sta:bs=2:sw=4:
