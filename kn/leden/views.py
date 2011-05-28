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
from django.core.urlresolvers import reverse
from os import path
from django.contrib.auth.views import redirect_to_login
from kn import settings
from hashlib import sha256
from datetime import date

# Create your views here.
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
