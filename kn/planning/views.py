# vim: et:sta:bs=2:sw=4:
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from kn.leden.mongo import _id
from kn.leden.date import date_to_dt
from kn.planning.forms import *
from kn.planning.entities import Pool, Worker, Event, Vacancy

from random import shuffle

def hm2s(hours, minutes=0):
    return (hours * 60 + minutes) * 60

templates = {
    '': { },
    'borrel': {
        'tappers': [
            [hm2s(20, 30), hm2s(23), 'eerste dienst'],
            [hm2s(23), hm2s(25), 'tweede dienst'],
            [hm2s(25), hm2s(28), 'derde dienst']],
        'bestuur': [
            [hm2s(20, 30), hm2s(24), 'openen'],
            [hm2s(24), hm2s(28), 'sluiten']],
        'draai': [
            [hm2s(20, 45), hm2s(23), 'openen'],
            [hm2s(23), hm2s(24), 'prime-time'],
            [hm2s(24), hm2s(25), 'sluiten']]},
    'kleinfeest': {
        'tappers': [
            [hm2s(20, 30), hm2s(23), 'eerste dienst'],
            [hm2s(23), hm2s(25), 'tweede dienst'],
            [hm2s(25), hm2s(28), 'derde dienst']],
        'bestuur': [
            [hm2s(20, 30), hm2s(24), 'openen'],
            [hm2s(24), hm2s(28), 'sluiten']]},
    'grootfeest': {
        'tappers': [
            [hm2s(20, 30), hm2s(23), 'eerste dienst, tapper 1'],
            [hm2s(20, 30), hm2s(23), 'eerste dienst, tapper 2'],
            [hm2s(23), hm2s(25), 'tweede dienst, tapper 1'],
            [hm2s(23), hm2s(25), 'tweede dienst, tapper 2'],
            [hm2s(25), hm2s(28), 'derde dienst, tapper 1'],
            [hm2s(25), hm2s(28), 'derde dienst, tapper 2']],
        'bestuur': [
            [hm2s(20, 30), hm2s(24), 'openen'],
            [hm2s(24), hm2s(28), 'sluiten']]},
    'dranktelling': {
        'barco': [
            [hm2s(20), hm2s(20, 30), 'Teller 1'],
            [hm2s(20), hm2s(20, 30), 'Teller 2']]},
    'dranklevering': {
        'barco': [
            [hm2s(10), hm2s(13), 'Persoon 1'],
            [hm2s(10), hm2s(13), 'Persoon 2']]},
}

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
                'begin': v.begin,
                'begin_time': v.begin_time,
                'end_time': v.end_time,
                'assignee': v.assignee.get_user().humanName
                        if v.assignee else "?"})
        for idx in poolid2idx.values():
            ei['vacancies'][idx].sort(key=lambda x: x['begin'])
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
    workers = Worker.all_in_pool(pool)
    # TODO reduce number of queries
    events = dict()
    for e in Event.all_in_future():
        eid = _id(e)
        vacancies = list(e.vacancies(pool=pool))
        if not vacancies:
            continue
        events[eid] = {'vacancies': vacancies, 'date': e.date.date(),
                'name': e.name, 'id': eid}
        posted = False
        events[eid]['vacancies'].sort(key=lambda v: v.begin)
        if request.method == 'POST' and _id(request.POST['eid']) == eid:
            events[eid]['form'] = ManagePlanningForm(request.POST, pool=pool,
                    vacancies=events[eid]['vacancies'])
            posted = True
        else:
            events[eid]['form'] = ManagePlanningForm(pool=pool,
                    vacancies=events[eid]['vacancies'])
        if posted and events[eid]['form'].is_valid():
            for vacancy in events[eid]['vacancies']:
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
    for eid in events:
        for vacancy in events[eid]['vacancies']:
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
    events = list(events.values())
    events.sort(key=lambda e: e['date'])
    return render_to_response('planning/manage.html',
               {'events': events},
               context_instance=RequestContext(request))

@login_required
def planning_poollist(request):
    pools = list(Pool.all())
    return render_to_response('planning/pools.html',
            {'pools': pools},
            context_instance=RequestContext(request))

@login_required
def event_create(request):
    if request.method == 'POST':
        form = EventCreateForm(request.POST)
        if form.is_valid():
            fd = form.cleaned_data
            day = date_to_dt(fd['date'])
            e = Event({
                'name': fd['name'],
                'date': day})
            e.save()
            for poolname, periods in templates[fd['template']].items():
                pool = Pool.by_name(poolname)
                for period in periods:
                    v = Vacancy({
                        'name': period[2],
                        'event': _id(e),
                        'begin': day + datetime.timedelta(seconds=period[0]),
                        'end': day + datetime.timedelta(seconds=period[1]),
                        'pool': _id(pool),
                        'assignee': None,
                    })
                    v.save()
            return HttpResponseRedirect(reverse('planning-event-edit',
                args=(e._id,)))
    else:
        form = EventCreateForm()
    return render_to_response('planning/event_create.html', {'form': form},
            context_instance=RequestContext(request))

@login_required
def event_edit(request, eventid):
    avform = None
    e = Event.by_id(eventid)
    if request.method == 'POST':
        if request.POST['action'] == 'remove_event':
            e.delete()
            return HttpResponseRedirect(reverse('planning-poollist'))
        elif request.POST['action'] == 'remove_vacancy':
            Vacancy.by_id(_id(request.POST['vacancy_id'])).delete()
            return HttpResponseRedirect(reverse('planning-event-edit',
                args=(eventid,)))
        elif request.POST['action'] == 'add_vacancy':
            avform = AddVacancyForm(request.POST)
            if avform.is_valid():
                fd = avform.cleaned_data
                day = e.date
                (begin_hour, begin_minute) = map(int, fd['begin'].split(':'))
                (end_hour, end_minute) = map(int, fd['end'].split(':'))
                begin = hm2s(begin_hour, begin_minute)
                end = hm2s(end_hour, end_minute)
                v = Vacancy({
                    'name': fd['name'],
                    'event': _id(e),
                    'begin': e.date + datetime.timedelta(seconds=begin),
                    'end': e.date + datetime.timedelta(seconds=end),
                    'pool': _id(fd['pool']),
                    'assignee': None,
                })
                v.save()
                return HttpResponseRedirect(reverse('planning-event-edit',
                    args=(eventid,)))
    if avform is None:
        avform = AddVacancyForm()
    pools = dict()
    for p in Pool.all():
        pools[_id(p)] = p
    vacancies = list()
    for v in e.vacancies():
        v.poolname = pools[v.pool_id].name
        v.assignee_text = str(v.assignee.get_user().name) if v.assignee else "-"
        v.vid = str(v._id)
        vacancies.append(v)
    vacancies.sort(key=lambda x: str(x.pool_id) + str(x.begin))
    return render_to_response('planning/event_edit.html',
            {'name': e.name, 'date': str(e.date.date()),
            'avform': avform, 'vacancies': vacancies},
            context_instance=RequestContext(request))
