from itertools import chain
from hashlib import sha256
from datetime import date
from glob import glob
from os import path

import mimetypes
import logging
import Image
import json
import re

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator, EmptyPage
from django.core.files.storage import default_storage
from django.core.servers.basehttp import FileWrapper
from django.core.exceptions import PermissionDenied
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
from django.template import RequestContext

from kn.leden.forms import ChangePasswordForm, AddUserForm, AddGroupForm
from kn.leden.auth import login_or_basicauth_required
from kn.leden.utils import find_name_for_user
from kn.leden.date import now, date_to_dt
from kn.leden.mongo import _id
from kn.leden import giedo

from kn.base._random import pseudo_randstr
from kn.base.http import redirect_to_referer
from kn.base.mail import render_then_email
from kn.base.text import humanized_enum

from kn.settings import DT_MIN, DT_MAX
from kn import settings

import kn.leden.entities as Es

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
    if type and not type in e.types:
        raise ValueError, "Entity is not a %s" % type
    if not type:
        type = e.type
    if not type in Es.TYPE_MAP:
        raise ValueError, "Unknown entity type"
    return globals()['_'+type+'_detail'](request, getattr(e, 'as_'+type)())

def _entity_detail(request, e):
    def _cmp(x,y):
        r = Es.relation_cmp_until(y,x)
        if r: return r
        r = cmp(unicode(x['with'].humanName),
                unicode(y['with'].humanName))
        if r: return r
        r = cmp(unicode(x['how'].humanName) if x['how'] else None,
            unicode(y['how'].humanName) if y['how'] else None)
        if r: return r
        return Es.relation_cmp_from(x,y)
    def _rcmp(x,y):
        r = Es.relation_cmp_until(y,x)
        if r: return r
        r = cmp(unicode(x['how'].humanName) if x['how'] else None,
            unicode(y['how'].humanName) if y['how'] else None)
        if r: return r
        r = cmp(unicode(x['who'].humanName),
                unicode(y['who'].humanName))
        if r: return r
        return Es.relation_cmp_from(x,y)
    related = sorted(e.get_related(), cmp=_cmp)
    rrelated = sorted(e.get_rrelated(), cmp=_rcmp)
    for r in chain(related, rrelated):
        r['may_end'] = Es.user_may_end_relation(request.user, r)
        r['id'] = r['_id']
        r['until_year'] = (None if r['until'] is None else
                    Es.date_to_year(r['until']))
        r['virtual'] = Es.relation_is_virtual(r)
    tags = [t.as_primary_type() for t in e.get_tags()]

    # mapping of year => set of members
    year_sets = {}
    for r in rrelated:
        year = r['until_year']
        if year is None:
            year = 'this'

        if not year in year_sets:
            year_sets[year] = set()
        year_sets[year].add(r['who'])

    year_counts = {}
    for year in year_sets:
        year_counts[year] = len(year_sets[year])

    ctx = {'related': related,
           'rrelated': rrelated,
           'year_counts': year_counts,
           'now': now(),
           'tags': sorted(tags, Es.entity_cmp_humanName),
           'object': e,
           'chiefs': [],
           'pipos': [],
           'reps': [] }
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
        groups.sort(cmp=lambda x,y: cmp(unicode(x.humanName),
                        unicode(y.humanName)))
        users = sorted(Es.users(), cmp=Es.entity_cmp_humanName)
        brands = sorted(Es.brands(), cmp=Es.entity_cmp_humanName)
        ctx.update({'users': users,
                'brands': brands,
                'groups': groups,
                'may_add_related': True,
                'may_add_rrelated': True})
    ctx['may_upload_smoel'] = request.user.may_upload_smoel_for(e)
    if e.is_tag:
        ctx.update({'tag_bearers': sorted(e.as_tag().get_bearers(),
                        cmp=Es.entity_cmp_humanName)})
    return ctx

def _user_detail(request, user):
    hasPhoto = default_storage.exists('%s.jpg' %
            path.join(settings.SMOELEN_PHOTOS_PATH,
                    str(user.name)))
    ctx = _entity_detail(request, user)
    ctx.update({
            'hasPhoto': hasPhoto,
            'photoWidth': settings.SMOELEN_WIDTH,
            'photosUrl': reverse('fotos', kwargs={'path':''})
                         + '?q=tag:'+str(user.name)})
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
    def _cmp(x,y):
        r = Es.relation_cmp_until(y,x)
        if r: return r
        r = cmp(unicode(x['with'].humanName),
                unicode(y['with'].humanName))
        if r: return r
        r = cmp(unicode(x['who'].humanName),
                unicode(y['who'].humanName))
        if r: return r
        return Es.relation_cmp_from(x,y)
    ctx['rels'] = sorted(Es.query_relations(how=brand, deref_who=True,
                deref_with=True), cmp=_cmp)
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
    def _cmp(s1, s2):
        r = Es.dt_cmp_until(s2['until'], s1['until'])
        if r: return r
        return cmp(s1['student'].humanName, s2['student'].humanName)
    for student in Es.by_study(study):
        for _study in student.studies:
            if _study['study'] != study:
                continue
            students.append({'student': student,
                             'from': _study['from'],
                             'until': _study['until'],
                             'institute': _study['institute']})
    ctx['students'].sort(cmp=_cmp)
    return render_to_response('leden/study_detail.html', ctx,
            context_instance=RequestContext(request))
def _institute_detail(request, institute):
    ctx = _entity_detail(request, institute)
    ctx['students'] = students = []
    def _cmp(s1, s2):
        r = Es.dt_cmp_until(s2['until'], s1['until'])
        if r: return r
        return cmp(s1['student'].humanName, s2['student'].humanName)
    for student in Es.by_institute(institute):
        for _study in student.studies:
            if _study['institute'] != institute:
                continue
            students.append({'student': student,
                             'from': _study['from'],
                             'until': _study['until'],
                             'study': _study['study']})
    ctx['students'].sort(cmp=_cmp)
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
        final_date = youngest.dateOfBirth.replace(year=youngest.dateOfBirth.year+18)
    return render_to_response('leden/entities_underage.html', {
                    'users': users,
                    'final_date': final_date},
            context_instance=RequestContext(request))

@login_required
def ik_chsmoel(request):
    if not 'smoel' in request.FILES:
        raise ValueError, "Missing `smoel' in FILES"
    if not 'id' in request.POST:
        raise ValueError, "Missing `id' in POST"
    user = Es.by_id(request.POST['id'])
    if not request.user.may_upload_smoel_for(request.user):
        raise PermissionDenied
    img = Image.open(request.FILES['smoel'])
    smoelen_width = settings.SMOELEN_WIDTH * 2
    img = img.resize((smoelen_width,
        int(float(smoelen_width) / img.size[0] * img.size[1])),
            Image.ANTIALIAS)
    img.save(default_storage.open(path.join(settings.SMOELEN_PHOTOS_PATH,
            str(user.name)) + ".jpg", 'w'), "JPEG")
    Es.notify_informacie('set_smoel', request.user, entity=user)
    return redirect_to_referer(request)

@login_required
def user_smoel(request, name):
    user = Es.by_name(name)
    if not user or not 'user' in user.types:
        raise Http404
    try:
        img = default_storage.open(path.join(
            settings.SMOELEN_PHOTOS_PATH,
            str(user.name)) + ".jpg")
    except IOError:
        raise Http404
    return HttpResponse(FileWrapper(img), mimetype="image/jpeg")

def _ik_chpasswd_handle_valid_form(request, form):
    oldpw = form.cleaned_data['old_password']
    newpw = form.cleaned_data['new_password']
    giedo.change_password(str(request.user.name), oldpw, newpw)
    t = """Lieve %s, maar natuurlijk, jouw wachtwoord is veranderd."""
    request.user.push_message(t % request.user.first_name)
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
            { 'form':form, 'errors':errstr},
            context_instance=RequestContext(request))

@login_required
def ik_chpasswd_villanet(request):
    errl = []
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            try:
                oldpw = form.cleaned_data['old_password']
                newpw = form.cleaned_data['new_password']
                giedo.change_villanet_password(str(request.user.name), oldpw,
                        newpw)
                t = ("Lieve %s, maar natuurlijk, jouw wachtwoord voor het "+
                        "villa-netwerk is veranderd.")
                request.user.push_message(t % request.user.first_name)
                return HttpResponseRedirect(reverse('smoelen-home'))
            except giedo.ChangePasswordError as e:
                errl.extend(e.args)
    else:
        form = ChangePasswordForm()
    errl.extend(form.non_field_errors())
    errstr = humanized_enum(errl)
    return render_to_response('leden/ik_chpasswd_villanet.html',
            { 'form':form, 'errors':errstr},
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
        if request.REQUEST['validate'] == token:
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
        if request.REQUEST['token'] == token:
            user = Es.by_name(request.REQUEST['user'])
            properties = {
                'firstname': user.first_name,
                'lastname': user.last_name,
                'gender': user.gender,
                'fullname': user.full_name,
                'groups': list(user.cached_groups_names)
            }
            return HttpResponse(json.dumps(dict([
                (k, properties[k]) for k in
                set(s.strip() for s in request.REQUEST.get('fetch').split(','))
                if k in properties
            ] )))
        return HttpResponse("INVALID TOKEN")
    if not request.user.is_authenticated():
        # De replace() is een workaround voor
        #   http://code.djangoproject.com/ticket/11457
        return redirect_to_login('%s?url=%s' % (
                reverse('rauth'),
                request.REQUEST['url'].replace('/', '%2F')))
    token = sha256('%s|%s|%s|%s' % (str(request.user.name),
                    date.today(),
                    request.REQUEST['url'],
                    settings.SECRET_KEY)).hexdigest()
    return HttpResponseRedirect('%s%suser=%s&token=%s' % (
        request.REQUEST['url'],
        '?' if request.REQUEST['url'].find('?') == -1 else '&',
        str(request.user.name), token))

def api_users(request):
    if not request.REQUEST['key'] in settings.ALLOWED_API_KEYS:
        raise PermissionDenied
    ret = {}
    for m in Es.users():
        ret[str(m.name)] = m.full_name
    return HttpResponse(json.dumps(ret), mimetype="text/json")

@login_required
def secr_add_user(request):
    if 'secretariaat' not in request.user.cached_groups_names:
        raise PermissionDenied
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            fd = form.cleaned_data
            nm = find_name_for_user(fd['first_name'],
                        fd['last_name'])
            # First, create the entity.
            u = Es.User({
                'types': ['user'],
                'names': [nm],
                'humanNames': [{'human': fd['first_name']+' '+
                             fd['last_name']}],
                'person': {
                    'titles': [],
                    'nick': fd['first_name'],
                    'given': None,
                    'family': fd['last_name'],
                    'gender': fd['sex'],
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
            logging.info("Added user %s" % nm)
            u.save()
            # Then, add the relations.
            Es.add_relation(u, Es.id_by_name('leden',
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
            render_then_email("leden/set-password.mail.txt",
                        u.canonical_full_email, {
                            'user': u,
                            'password': pwd})
            # Send the welcome e-mail
            render_then_email("leden/welcome.mail.txt",
                        u.canonical_full_email, {
                            'u': u})
            Es.notify_informacie('adduser', request.user, entity=u._id)
            return HttpResponseRedirect(reverse('user-by-name',
                    args=(nm,)))
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
            request.user.push_message("Groep toegevoegd.")
            return HttpResponseRedirect(reverse('group-by-name', args=(nm,)))
    else:
        form = AddGroupForm()
    return render_to_response('leden/secr_add_group.html', {'form': form},
            context_instance=RequestContext(request))

@login_required
def relation_end(request, _id):
    rel = Es.relation_by_id(_id)
    if rel is None:
        raise Http404
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
            raise ValueError, "Missing attr %s" % t
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
        raise ValueError, "This relation already exists"

    # Add the relation!
    relation_id = Es.add_relation(d['who'], d['with'], d['how'], dt, DT_MAX)

    # Notify informacie
    # TODO (rik) leave out 'als lid'
    Es.notify_informacie('relation_begin', request.user, relation=relation_id)

    giedo.sync_async(request)
    return redirect_to_referer(request)

@login_required
def user_reset_password(request, _id):
    if not 'secretariaat' in request.user.cached_groups_names:
        raise PermissionDenied
    u = Es.by_id(_id).as_user()
    pwd = pseudo_randstr()
    u.set_password(pwd)
    giedo.change_password(str(u.name), pwd, pwd)
    render_then_email("leden/reset-password.mail.txt",
                        u.canonical_full_email, {
                            'user': u,
                            'password': pwd})
    request.user.push_message("Wachtwoord gereset!")
    return redirect_to_referer(request)

@login_required
def note_add(request):
    if not 'secretariaat' in request.user.cached_groups_names:
        raise PermissionDenied
    if 'on' not in request.POST or 'note' not in request.POST:
        raise ValueError, "missing `on' or `note'"
    on = Es.by_id(_id(request.POST['on']))
    if on is None:
        raise Http404
    on.add_note(request.POST['note'], request.user)
    render_then_email("leden/new-note.mail.txt",
                        Es.by_name('secretariaat').canonical_full_email, {
                            'user': request.user,
                            'note': request.POST['note'],
                            'on': on})
    return redirect_to_referer(request)

@login_required
def secr_update_site_agenda(request):
        if 'secretariaat' not in request.user.cached_groups_names:
                raise PermissionDenied
        giedo.update_site_agenda()
        request.user.push_message("Agenda geupdate!")
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
            request.user.push_message("Je verzoek wordt verwerkt. "+
                "Verwacht binnen 5 minuten een e-mail.")
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
    response = HttpResponse(FileWrapper(default_storage.open(p)),
            mimetype=mimetypes.guess_type(default_storage.path(p))[0])
    response['Content-Length'] = default_storage.size(p)
    # XXX use ETags and returns 304's
    return response

# vim: et:sta:bs=2:sw=4:
