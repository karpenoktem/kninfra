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
		if not vacancy.date in days:
			days[vacancy.date] = {'vacancies': list()}
		days[vacancy.date]['vacancies'].append(vacancy)

	for day in days:
		posted = False
		days[day]['vacancies'].sort(key=lambda v: v.begin)
		if request.method == 'POST' and request.POST['date'] == day:
			days[day]['form'] = ManagePlanningForm(request.POST)
			posted = True
		else:
			days[day]['form'] = ManagePlanningForm()
		for vacancy in days[day]['vacancies']:
			days[day]['form'].__setattr__('shift_%s' % vacancy._id, EntityChoiceField(label="Wie", choices=Es.users(), sort_choices=True))
		if posted and days[day]['form'].is_valid():
			print "XXX"

	return render_to_response('planning/manage.html', {'days': days}, context_instance=RequestContext(request))
