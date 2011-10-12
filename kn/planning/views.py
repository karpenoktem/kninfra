from django.http import Http404
from django.template import RequestContext
from kn.planning.forms import *
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from kn.planning.entities import Pool, Worker, Vacancy

@login_required
def planning_manage(request, poolname):
	pool = Pool.by_name(poolname)
	if pool is None:
		raise Http404
	upcoming_vacancies = pool.vacancies()
	workers = Worker.all_in_pool(pool)
	days = dict()
	for vacancy in upcoming_vacancies:
		date = vacancy.date.date().__str__()
		if not date in days:
			days[date] = {'vacancies': list()}
		days[date]['vacancies'].append(vacancy)

	for day in days:
		posted = False
		days[day]['vacancies'].sort(key=lambda v: v.begin)
		if request.method == 'POST' and request.POST['date'] == day:
			days[day]['form'] = ManagePlanningForm(request.POST, vacancies=days[day]['vacancies'])
			posted = True
		else:
			days[day]['form'] = ManagePlanningForm(vacancies=days[day]['vacancies'])
		if posted and days[day]['form'].is_valid():
			print days[day]['form'].cleaned_data
			for vacancy in days[day]['vacancies']:
				worker = request.POST['shift_%s' % vacancy._id]
				worker = Es.by_id(worker)
				print list(worker.names)
				vacancy.assignee = worker
				vacancy.save()

	print days
	return render_to_response('planning/manage.html', {'days': days}, context_instance=RequestContext(request))
