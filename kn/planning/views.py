# vim: et:sta:bs=2:sw=4:
import locale
from random import shuffle

from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from kn.leden.mongo import _id
from kn.leden.date import date_to_dt, now
from kn.base.http import JsonHttpResponse
from kn.planning.forms import *
from kn.planning.entities import Pool, Worker, Event, Vacancy
from kn.planning.score import planning_vacancy_worker_score
from kn.planning.utils import send_reminder

def hm2s(hours, minutes=0):
    return (hours * 60 + minutes) * 60

templates = {
    '': { },
    'borrel': {
        'tappers': [
            [(hm2s(20, 30),False), (hm2s(23),False), 'eerste dienst'],
            [(hm2s(23),False), (hm2s(25),False), 'tweede dienst'],
            [(hm2s(25),False), (hm2s(28),True), 'derde dienst']],
        'bestuur': [
            [(hm2s(20, 30),False), (hm2s(24),False), 'openen'],
            [(hm2s(24),False), (hm2s(28),True), 'sluiten']],
        'draai': [
            [(hm2s(20, 45),False), (hm2s(23),False), 'openen'],
            [(hm2s(23),False), (hm2s(24),False), 'prime-time'],
            [(hm2s(24),False), (hm2s(25),True), 'sluiten']]},
    'kleinfeest': {
        'tappers': [
            [(hm2s(20, 30),False), (hm2s(23),False), 'eerste dienst'],
            [(hm2s(23),False), (hm2s(25),False), 'tweede dienst'],
            [(hm2s(25),False), (hm2s(28),True), 'derde dienst']],
        'bestuur': [
            [(hm2s(20, 30),False), (hm2s(24),False), 'openen'],
            [(hm2s(24),False), (hm2s(28),True), 'sluiten']]},
    'grootfeest': {
        'tappers': [
            [(hm2s(20, 30),False), (hm2s(23),False), 'eerste dienst, tapper 1'],
            [(hm2s(20, 30),False), (hm2s(23),False), 'eerste dienst, tapper 2'],
            [(hm2s(23),False), (hm2s(25),False), 'tweede dienst, tapper 1'],
            [(hm2s(23),False), (hm2s(25),False), 'tweede dienst, tapper 2'],
            [(hm2s(25),False), (hm2s(28),True), 'derde dienst, tapper 1'],
            [(hm2s(25),False), (hm2s(28),True), 'derde dienst, tapper 2']],
        'bestuur': [
            [(hm2s(20, 30),False), (hm2s(24),False), 'openen'],
            [(hm2s(24),False), (hm2s(28),True), 'sluiten']]},
    'dranktelling': {
        'barco': [
            [(hm2s(20),True), (hm2s(20, 30),False), 'Teller 1'],
            [(hm2s(20),True), (hm2s(20, 30),False), 'Teller 2']]},
    'dranklevering': {
        'barco': [
            [(hm2s(9),False), (hm2s(13),False), 'Persoon 1'],
            [(hm2s(9),False), (hm2s(13),False), 'Persoon 2']]},
    'vrijdag_met_tappers': {
        'tappers': [
            [(hm2s(20, 30),False), (hm2s(23),False), 'eerste dienst'],
            [(hm2s(23),False), (hm2s(25),False), 'tweede dienst'],
            [(hm2s(25),False), (hm2s(28),True), 'derde dienst']],
        'bestuur': [
            [(hm2s(20, 30),False), (hm2s(24),False), 'openen'],
            [(hm2s(24),False), (hm2s(28),True), 'sluiten']]},
    'vrijdag_zonder_tappers': {
        'bestuur': [
            [(hm2s(20, 30),False), (hm2s(24),False), 'openen'],
            [(hm2s(24),False), (hm2s(28),True), 'sluiten']]},
}

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
                'kind': e.kind,
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

# extends cmp with None as bottom
def cmp_None(x,y,cmp=cmp):
    if x==None:
        return -1
    if y==None:
        return 1
    return cmp(x,y)

@login_required
def planning_manage(request, poolname):
    pool = Pool.by_name(poolname)
    if pool is None:
        raise Http404
    if not request.user.cached_groups_names & set(['secretariaat',
        pool.administrator]):
        raise PermissionDenied
    # TODO reduce number of queries
    events = dict()
    for e in Event.all_in_future():
        eid = _id(e)
        vacancies = list(e.vacancies(pool=pool))
        events[eid] = {'vacancies': vacancies, 'date': e.date.date(),
                'name': e.name, 'kind': e.kind, 'id': eid}
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
                    vacancy.reminder_needed = True
                else:
                    if vacancy.assignee_id == None or \
                            _id(vacancy.assignee_id) != _id(worker):
                        delta = datetime.timedelta(days=5)
                        vacancy.reminder_needed = now() + delta < e.date
                        vacancy.assignee_id = _id(worker)
                vacancy.save()
    workers = list(Worker.all_in_pool(pool))
    for worker in workers:
        # XXX het is cooler de shift dichtstbijzijnd aan de vacancy te
        # zoeken.  Stel dat iemand over een half-jaar al is ingepland
        # dan is dat niet zo boeiend.  Terwijl hij nu geen enkele
        # bardienst meer zou krijgen
        worker.set_last_shift(pool)
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
            found_scores = list(workers_by_score.keys())
            found_scores.sort(reverse=True)
            for score in found_scores:
                scorers = workers_by_score[score]
                shuffle(scorers)
                scorers.sort(key=lambda x: x.last_shift,
                        cmp=cmp_None)
                for scorer in scorers:
                    vacancy.suggestions.append({'scorer': scorer, 'score': score})

    events = list(events.values())
    events.sort(key=lambda e: e['date'])
    return render_to_response('planning/manage.html',
            {'events': events, 'pool': poolname},
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
                'date': day,
                'kind': fd['template']})
            e.save()
            for poolname, periods in templates[fd['template']].items():
                pool = Pool.by_name(poolname)
                for period in periods:
                    begin_date = day + datetime.timedelta(seconds=period[0][0])
                    end_date = day + datetime.timedelta(seconds=period[1][0])
                    v = Vacancy({
                        'name': period[2],
                        'event': _id(e),
                        'begin': (begin_date, period[0][1]),
                        'end': (end_date, period[1][1]) ,
                        'pool': _id(pool),
                        'assignee': None,
                        'reminder_needed': True,
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
            for vacancy in e.vacancies():
                vacancy.delete()
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
                begin_offset = hm2s(begin_hour, begin_minute)
                end_offset = hm2s(end_hour, end_minute)
                begin_date = e.date + datetime.timedelta(seconds=begin_offset)
                end_date = e.date + datetime.timedelta(seconds=end_offset)
                v = Vacancy({
                    'name': fd['name'],
                    'event': _id(e),
                    'begin': (begin_date, fd['begin_is_approximate']=="True"),
                    'end': (end_date, fd['end_is_approximate']=="True"),
                    'pool': _id(fd['pool']),
                    'assignee': None,
                    'reminder_needed': True,
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
            {'name': e.name, 'kind': e.kind, 'date': str(e.date.date()),
            'avform': avform, 'vacancies': vacancies},
            context_instance=RequestContext(request))

def _api_send_reminder(request):
    if not 'vacancy_id' in request.REQUEST:
        return JsonHttpResponse({'error': 'missing argument'})
    v = Vacancy.by_id(request.REQUEST['vacancy_id'])
    if not v:
        raise Http404
    print v._data
    print v.pool_id
    print v.pool
    if not request.user.cached_groups_names & set(['secretariaat',
        v.pool.administrator]):
        raise PermissionDenied
    send_reminder(v, update=False)
    return JsonHttpResponse({'success': True})

@login_required
def planning_api(request):
    locale.setlocale(locale.LC_ALL, 'nl_NL')
    action = request.REQUEST.get('action')
    if action == 'send-reminder':
        return _api_send_reminder(request)
    else:
        return JsonHttpResponse({'error': 'unknown action'})

@login_required
def planning_template(request, poolname):
    locale.setlocale(locale.LC_ALL, 'nl_NL')
    pool = Pool.by_name(poolname)
    events = list()
    # TODO reduce number of queries
    for e in Event.all_in_future():
        vacancies = list(e.vacancies(pool))
        if not vacancies:
            continue
        ei = {  'name': e.name,
                'date': str(e.date.date()),
            'vacancies': list()}
        ei['description'] = e.date.strftime('%A %d %B')
        if e.name != 'Borrel':
            ei['description'] = '%s (%s)' % (ei['description'], ei['name'])
        shifts = dict()
        for v in vacancies:
            if not v.begin in shifts:
                shifts[v.begin] = {
                    'name': v.name,
                    'begin': v.begin,
                    'begin_time': v.begin_time,
                    'end_time': v.end_time,
                    'assignees': list()}
            shifts[v.begin]['assignees'].append(v.assignee)
        ei['vacancies'] = map(lambda x: x[1], sorted(shifts.items(),
            key=lambda x: x[0]))
        events.append(ei)
    events.sort(key=lambda x: x['date'])
    return render_to_response('planning/template.html', {'events': events},
            context_instance=RequestContext(request))
