from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from kn.base.text import humanized_enum
from kn.leden.forms import ChangePasswordForm, AddUserForm
from kn.leden.utils import find_name_for_user
from kn.leden import giedo
from kn.leden.mongo import _id
from kn.leden.date import now, date_to_dt
from kn.base.http import redirect_to_referer
from kn import settings
from kn.settings import DT_MIN, DT_MAX
from kn.base._random import pseudo_randstr
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from os import path
from itertools import chain
from django.contrib.auth.views import redirect_to_login
from kn import settings
from hashlib import sha256
from datetime import date
import json
import logging

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
	ctx = {'related': related,
	       'rrelated': rrelated,
               'now': now(),
	       'tags': sorted(tags, Es.entity_cmp_humanName),
	       'object': e}
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
        if e.is_tag:
                ctx.update({'tag_bearers': sorted(e.as_tag().get_bearers(),
                                                cmp=Es.entity_cmp_humanName)})
        return ctx

def _user_detail(request, user):
	hasPhoto = default_storage.exists('%s.jpg' % 
			path.join(settings.SMOELEN_PHOTOS_PATH,
					str(user.name)))
	ctx = _entity_detail(request, user)
	ctx.update({'hasPhoto': hasPhoto,
                    'photosUrl': settings.USER_PHOTOS_URL % str(user.name)})
	return render_to_response('leden/user_detail.html', ctx,
			context_instance=RequestContext(request))

def _group_detail(request, group):
	ctx = _entity_detail(request, group)
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
	# TODO add followers in ctx
	return render_to_response('leden/study_detail.html', ctx,
			context_instance=RequestContext(request))
def _institute_detail(request, institute):
	ctx = _entity_detail(request, institute)
	# TODO add followers in ctx
	return render_to_response('leden/institute_detail.html', ctx,
			context_instance=RequestContext(request))

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

def rauth(request):
	""" An implementation of Jille Timmermans' rauth scheme """
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
	if not request.user.is_authenticated():
		# De replace() is een workaround voor
		#	http://code.djangoproject.com/ticket/11457
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
                        Es.add_relation(u, Es.id_by_name('leden',
                                                        use_cache=True),
                                        _from=date_to_dt(fd['dateJoined']))
                        Es.add_relation(u, Es.id_by_name('aan', use_cache=True),
                                        _from=now())
                        giedo.sync()
                        request.user.push_message("Gebruiker toegevoegd. "+
                                "Let op: hij heeft geen wachtwoord "+
                                "en hij moet nog gemaild worden.")
                        return HttpResponseRedirect(reverse('user-by-name',
                                        args=(nm,)))
        else:
                form = AddUserForm()
	return render_to_response('leden/secr_add_user.html',
                        {'form': form},
			context_instance=RequestContext(request))

@login_required
def relation_end(request, _id):
        rel = Es.relation_by_id(_id)
        if rel is None:
                raise Http404
        if not Es.user_may_end_relation(request.user, rel):
                raise PermissionDenied
        Es.end_relation(_id)
        giedo.sync()
        return redirect_to_referer(request)

@login_required
def relation_begin(request):
        # TODO We should use Django forms, or better: use sweet Ajax
        if not 'secretariaat' in request.user.cached_groups_names:
                raise PermissionDenied
        d = {}
        for t in ('who', 'with', 'how'):
                if t not in request.POST:
                        raise ValueError, "Missing attr %s" % t
                if t == 'how' and request.POST[t] == 'null':
                        d[t] = None
                else:
                        d[t] = _id(request.POST[t])
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
        Es.add_relation(d['who'], d['with'], d['how'], dt, DT_MAX)
        giedo.sync()
        return redirect_to_referer(request)

@login_required
def user_reset_password(request, _id):
        if not 'secretariaat' in request.user.cached_groups_names:
                raise PermissionDenied
        u = Es.by_id(_id).as_user()
        pwd = pseudo_randstr()
        u.set_password(pwd)
        giedo.change_password(str(u.name), pwd, pwd)
        email = EmailMessage(
                "[KN] Nieuw wachtwoord",
                ("Beste %s,\n\n"+
                 "Jouw wachtwoord is gereset.  Je kunt inloggen met:\n"+
                 "  gebruikersnaam     %s\n"+
                 "  wachtwoord         %s\n\n"+
                 "Met een vriendelijke groet,\n\n"+
                 "  Het Karpe Noktem Smoelenboek") % (
                          u.first_name, str(u.name), pwd),
                'Karpe Noktem\'s ledenadministratie <root@karpenoktem.nl>',
                [u.canonical_email])
        email.send()
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
        email = EmailMessage(
                "Nieuwe notitie",
                "Door %s is de volgende notitie geplaatst op %s:\r\n\r\n%s" % (
                        request.user.full_name, unicode(on.humanName),
                        request.POST['note']),
                'Karpe Noktem\'s ledenadministratie <root@karpenoktem.nl>',
                [Es.by_name('secretariaat').canonical_email]).send()
        return redirect_to_referer(request)
