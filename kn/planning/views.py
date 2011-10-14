from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.template import RequestContext
from kn.leden.mongo import _id
from kn.planning.forms import *
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from kn.planning.entities import Pool, Worker, Vacancy

@login_required
def planning_manage(request, poolname):
	pool = Pool.by_name(poolname)
	if pool is None:
		raise Http404
	if pool.administrator not in request.user.cached_groups_names and 'secretariaat' not in request.user.cached_groups_names:
		raise PermissionDenied
	upcoming_vacancies = pool.vacancies()
	workers = Worker.all_in_pool(pool)
	# XXX groeperen op Event ipv op datum
	days = dict()
	for vacancy in upcoming_vacancies:
		date = vacancy.event.date.date().__str__()
		if not date in days:
			days[date] = {'vacancies': list()}
		days[date]['vacancies'].append(vacancy)

	for day in days:
		posted = False
		days[day]['vacancies'].sort(key=lambda v: v.begin)
		if request.method == 'POST' and request.POST['date'] == day:
			days[day]['form'] = ManagePlanningForm(request.POST, pool=pool, vacancies=days[day]['vacancies'])
			posted = True
		else:
			days[day]['form'] = ManagePlanningForm(pool=pool, vacancies=days[day]['vacancies'])
		if posted and days[day]['form'].is_valid():
			print days[day]['form'].cleaned_data
			for vacancy in days[day]['vacancies']:
				worker = request.POST['shift_%s' % vacancy._id]
				if worker == '':
					vacancy.assignee = None
				else:
					vacancy.assignee_id = _id(worker)
				vacancy.save()

	return render_to_response('planning/manage.html', {'days': days}, context_instance=RequestContext(request))

@login_required
def planning_poollist(request):
	pools = list(Pool.all())
	return render_to_response('planning/pools.html', {'pools': pools}, context_instance=RequestContext(request))
