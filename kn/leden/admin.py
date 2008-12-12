from django.shortcuts import render_to_response, get_object_or_404
from models import Study, KnUser, EduInstitute, KnGroup, Seat, Alias
from django.template import RequestContext
from django.contrib.auth.admin import AdminPasswordChangeForm, UserAdmin
from django.utils.html import escape
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext, ugettext_lazy as _

class KnUserAdmin(admin.ModelAdmin):
	change_password_form = AdminPasswordChangeForm
	list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
	list_filter = ('is_staff', 'is_superuser')
	search_fields = ('username', 'first_name', 'last_name', 'email')
	ordering = ('username', )
	filter_horizontal = ('user_permissions',)
	
	def __call__(self, request, url):
		if url is None:
			return self.changelist_view(request)
		if url.endswith('password'):
			return HttpResponseRedirect('../../../../auth/user/%s/password' %
					url.split('/')[0])
		return super(KnUserAdmin, self).__call__(request, url)

class KnGroupAdmin(admin.ModelAdmin):
	search_fields = ('name', 'description')
	ordering = ('name', )
	filter_horizontal = ('permissions', )
	list_display = ('name', 'humanName')

admin.site.register(Study)
admin.site.register(KnUser, KnUserAdmin)
admin.site.register(EduInstitute)
admin.site.register(KnGroup, KnGroupAdmin)
admin.site.register(Seat)
admin.site.register(Alias)
