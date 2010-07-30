from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from kn.base.text import humanized_enum
from kn.leden.models import OldKnGroup, OldKnUser
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
def entity_detail(request, name=None, _id=None):
	if name is not None:
		e = Es.by_name(name)
	else:
		e = Es.by_id(_id)
	if e is None:
		raise Http404
	if e.type == 'user':
		return _user_detail(request, e.as_user())
	elif e.type == 'group':
		return _group_detail(request, e.as_group())
	elif e.type == 'tag':
		return _tag_detail(request, e.as_tag())
	elif e.type == 'seat':
		return _seat_detail(request, e.as_seat())
	elif e.type == 'study':
		return _study_detail(request, e.as_study())
	elif e.type == 'institute':
		return _institute_detail(request, e.as_institute())
	raise ValueError, "Unknown entity type"

def _entity_detail(request, e):
	def _cmp(x,y):
		r = cmp(x['until'], y['until'])
		if r: return r
		r = cmp(x['with'].humanName, y['with'].humanName)
		if r: return r
		return cmp(x['from'], y['from'])
	related = sorted(e.get_related(), cmp=_cmp)
	return {'related': related,
		'object': e}

def _user_detail(request, user):
	# TODO stub
	return HttpResponse("")
def _group_detail(request, group):
	# TODO stub
	return HttpResponse("")
def _tag_detail(request, tag):
	# TODO stub
	return HttpResponse("")
def _seat_detail(request, seat):
	# TODO stub
	return HttpResponse("")
def _study_detail(request, study):
	# TODO stub
	return HttpResponse("")
def _institute_detail(request, institute):
	# TODO stub
	return HttpResponse("")


# ----------------
# Unconverted
# ----------------
@login_required
def oldknuser_detail(request, name):
	try:
		user = OldKnUser.objects.select_related('oldseat_set',
				'groups').get(username=name)
	except OldKnUser.DoesNotExist:
		raise Http404
	oldseats = list(user.oldseat_set.select_related('group').all())
	oldseats.sort(lambda x,y: cmp(x.humanName, y.humanName))
	comms = filter(lambda x: not x.isHidden,
			map(lambda x: x.oldkngroup, user.groups.all()))
	comms.sort(lambda x,y: cmp(x.humanName, y.humanName))
	hasPhoto = default_storage.exists('%s.jpg' % 
			path.join(settings.SMOELEN_PHOTOS_PATH,
					user.username))
	return render_to_response('leden/oldknuser_detail.html',
			{'object': user,
			 'oldseats': oldseats,
			 'comms': comms,
			 'photosUrl': settings.USER_PHOTOS_URL % name,
			 'hasPhoto': hasPhoto},
			context_instance=RequestContext(request))

@login_required
def oldkngroup_detail(request, name):
	try:
		group = OldKnGroup.objects.select_related('oldseat_set',
				'user_set').order_by('humanName').get(name=name)
	except OldKnGroup.DoesNotExist:
		raise Http404
	otherMembers = list()
	subGroups = filter(lambda x: not x.isHidden,
			group.oldkngroup_set.order_by('humanName').all())
	oldseats = list(group.oldseat_set.order_by('humanName').all())
	oldseat_ids = frozenset(map(lambda x: x.user_id, oldseats))
	for user in group.user_set.select_related('oldknuser'
			).order_by('first_name').all():
		if user.id in oldseat_ids:
			continue
		otherMembers.append(user)
	return render_to_response('leden/oldkngroup_detail.html',
			{'object': group,
		 	 'oldseats': oldseats,
			 'subGroups': subGroups,
			 'otherMembers': otherMembers},
			context_instance=RequestContext(request))

@login_required
def oldknuser_smoel(request, name):
	try:
		user = OldKnUser.objects.get(username=name)
	except OldKnUser.DoesNotExist:
		raise Http404
	try:
		img = default_storage.open(path.join(
			settings.SMOELEN_PHOTOS_PATH,
			user.username) + ".jpg")
	except IOError:
		raise Http404
	return HttpResponse(FileWrapper(img), mimetype="image/jpeg")

def ik_chpasswd_handle_valid_form(request, form):
	oldpw = form.cleaned_data['old_password']
	newpw = form.cleaned_data['new_password']
	change_password(request.user.username, oldpw, newpw)
	t = """Lieve %s, maar natuurlijk, jouw wachtwoord is veranderd.""" 
	request.user.message_set.create(message=(t % request.user.first_name))
	return HttpResponseRedirect(reverse('smoelen-home'))

@login_required
def ik_chpasswd(request):
	errl = []
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST) 
		if form.is_valid():
			try:
				return ik_chpasswd_handle_valid_form(request, 
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
	token = sha256('%s|%s|%s|%s' % (request.user.username,
					date.today(),
					request.REQUEST['url'],
					settings.SECRET_KEY)).hexdigest()
	return HttpResponseRedirect('%s%suser=%s&token=%s' % (
		request.REQUEST['url'],
		'?' if request.REQUEST['url'].find('?') == -1 else '&',
		request.user.username, token))
