from django.http import Http404
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from kn.leden.mongo import _id
from kn.planning.forms import *
from kn.planning.entities import Pool, Worker, Event, Vacancy

from random import shuffle

def planning_vacancy_worker_score(vacancy, worker):
	return 50

@login_required
def planning_view(request):
	pools = list(Pool.all())
	poolid2idx = dict()
	i = 0
	for pool in pools:
		poolid2idx[pool._id] = i
		i += 1
	events = list()
        # TODO reduce number of queries
	for e in Event.all_in_future():
		ei = {  'name': e.name,
		        'date': str(e.date.date()),
			'vacancies': dict()}
		for idx in poolid2idx.values():
			ei['vacancies'][idx] = list()
		for v in e.vacancies():
			ei['vacancies'][poolid2idx[v.pool_id]].append({
				'begin_time': v.begin_time,
				'end_time': v.end_time,
				'assignee': v.assignee.get_user().humanName
                                                if v.assignee else "?"})
		for idx in poolid2idx.values():
			ei['vacancies'][idx].sort()
		events.append(ei)
	events.sort(key=lambda x: x['date'])
	return render_to_response('planning/overview.html',
                        {'events': events,
                         'pools': pools,
                         'poolcount': len(pools)},
                        context_instance=RequestContext(request))

@login_required
def planning_manage(request, poolname):
	pool = Pool.by_name(poolname)
	if pool is None:
		raise Http404
	if (pool.administrator not in request.user.cached_groups_names
                and 'secretariaat' not in request.user.cached_groups_names):
		raise PermissionDenied
	upcoming_vacancies = pool.vacancies()
	workers = Worker.all_in_pool(pool)
	# XXX groeperen op Event ipv op datum
	days = dict()
	for vacancy in upcoming_vacancies:
		date = str(vacancy.event.date.date())
		if not date in days:
			days[date] = {'vacancies': list()}
		days[date]['vacancies'].append(vacancy)
	for day in days:
		posted = False
		days[day]['vacancies'].sort(key=lambda v: v.begin)
		if request.method == 'POST' and request.POST['date'] == day:
			days[day]['form'] = ManagePlanningForm(request.POST,
                                        pool=pool,
                                        vacancies=days[day]['vacancies'])
			posted = True
		else:
			days[day]['form'] = ManagePlanningForm(pool=pool,
                                        vacancies=days[day]['vacancies'])
		if posted and days[day]['form'].is_valid():
			for vacancy in days[day]['vacancies']:
				worker = request.POST['shift_%s' % vacancy._id]
				if worker == '':
					vacancy.assignee = None
				else:
					vacancy.assignee_id = _id(worker)
				vacancy.save()
	workers = list(Worker.all_in_pool(pool))
	for worker in workers:
		# XXX het is cooler de shift dichtstbijzijnd aan de vacancy te
                # zoeken.  Stel dat iemand over een half-jaar al is ingepland
                # dan is dat niet zo boeiend.  Terwijl hij nu geen enkele
                # bardienst meer zou krijgen
		worker.gather_last_shift()
	for day in days:
		for vacancy in days[day]['vacancies']:
			vacancy.suggestions = list()
			workers_by_score = dict()
			for worker in workers:
				score = planning_vacancy_worker_score(vacancy,
                                                                        worker)
				if score not in workers_by_score:
					workers_by_score[score] = list()
				workers_by_score[score].append(worker)
			for score, scorers in workers_by_score.items():
				shuffle(scorers)
				scorers.sort(key=lambda x: x.last_shift)
				vacancy.suggestions.extend(scorers)
	return render_to_response('planning/manage.html',
                       {'days': days},
                       context_instance=RequestContext(request))

@login_required
def planning_poollist(request):
	pools = list(Pool.all())
	return render_to_response('planning/pools.html',
                        {'pools': pools},
                        context_instance=RequestContext(request))
