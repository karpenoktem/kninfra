from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from kn.base.text import humanized_enum
from kn.leden.forms import ChangePasswordForm
from kn.leden.utils import change_password, ChangePasswordError
from kn import settings
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.servers.basehttp import FileWrapper
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from os import path
from django.contrib.auth.views import redirect_to_login
from kn import settings
from hashlib import sha256
from datetime import date

import kn.leden.entities as Es

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
		r = cmp(x['until'], y['until'])
		if r: return r
		r = cmp(x['with'].humanName, y['with'].humanName)
		if r: return r
		return cmp(x['from'], y['from'])
	def _rcmp(x,y):
		r = cmp(x['until'], y['until'])
		if r: return r
		r = cmp(x['how'].humanName if x['how'] else None,
			y['how'].humanName if y['how'] else None)
		if r: return r
		r = cmp(x['who'].humanName, y['who'].humanName)
		if r: return r
		return cmp(x['from'], y['from'])
	related = sorted(e.get_related(), cmp=_cmp)
	rrelated = sorted(e.get_rrelated(), cmp=_rcmp)
	tags = list(e.get_tags())
	return {'related': related,
		'rrelated': rrelated,
		'tags': tags,
		'object': e}

def _user_detail(request, user):
	hasPhoto = default_storage.exists('%s.jpg' % 
			path.join(settings.SMOELEN_PHOTOS_PATH,
					user.primary_name))
	ctx = _entity_detail(request, user)
	ctx.update({'hasPhoto': hasPhoto})
	return render_to_response('leden/user_detail.html', ctx,
			context_instance=RequestContext(request))

def _group_detail(request, group):
	ctx = _entity_detail(request, group)
	return render_to_response('leden/group_detail.html', ctx,
			context_instance=RequestContext(request))

def _tag_detail(request, tag):
	ctx = _entity_detail(request, tag)
	ctx.update({'bearers': tag.get_bearers()})
	return render_to_response('leden/tag_detail.html', ctx,
			context_instance=RequestContext(request))
def _seat_detail(request, seat):
	# TODO stub
	return HttpResponse("")
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
			user.primary_name) + ".jpg")
	except IOError:
		raise Http404
	return HttpResponse(FileWrapper(img), mimetype="image/jpeg")

def _ik_chpasswd_handle_valid_form(request, form):
	oldpw = form.cleaned_data['old_password']
	newpw = form.cleaned_data['new_password']
	change_password(request.user.primary_name, oldpw, newpw)
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
			except ChangePasswordError as e:
				errl.extend(e.args)
	else:
		form = ChangePasswordForm()
	errl.extend(form.non_field_errors())
	errstr = humanized_enum(errl) 
	return render_to_response('leden/ik_chpasswd.html', 
			{ 'form':form, 'errors':errstr, 
				'user':request.user })

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
	token = sha256('%s|%s|%s|%s' % (request.user.primary_name,
					date.today(),
					request.REQUEST['url'],
					settings.SECRET_KEY)).hexdigest()
	return HttpResponseRedirect('%s%suser=%s&token=%s' % (
		request.REQUEST['url'],
		'?' if request.REQUEST['url'].find('?') == -1 else '&',
		request.user.primary_name, token))
