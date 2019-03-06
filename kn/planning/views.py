import datetime
from random import shuffle

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_POST

from kn.base.http import JsonHttpResponse, get_param
from kn.leden.date import date_to_dt, date_to_midnight, now
from kn.leden.entities import DT_MIN
from kn.leden.mongo import _id
from kn.planning.entities import Event, Pool, Vacancy, may_manage_planning
from kn.planning.forms import (AddVacancyForm, EventCreateForm,
                               ManagePlanningForm)
from kn.planning.score import planning_vacancy_worker_score
from kn.planning.utils import send_reminder


def hm2s(hours, minutes=0):
    return (hours * 60 + minutes) * 60


templates = {
    '': {},
    'borrel': {
        'tappers': [
            [(hm2s(20, 30), False), (hm2s(23), False), _('eerste dienst')],
            [(hm2s(23), False), (hm2s(25), False), _('tweede dienst')],
            [(hm2s(25), False), (hm2s(28), True), _('derde dienst')]],
        'sooscie': [
            [(hm2s(20, 30), False), (hm2s(24), False), _('openen')],
            [(hm2s(24), False), (hm2s(28), True), _('sluiten')]]},
      'borrel_met_avondeten': {
        'tappers': [
			[(hm2s(19), False), (hm2s(21), False), _('nulde dienst')],
            [(hm2s(21), False), (hm2s(23), False), _('eerste dienst')],
            [(hm2s(23), False), (hm2s(25), False), _('tweede dienst')],
            [(hm2s(25), False), (hm2s(28), True), _('derde dienst')]],
        'sooscie': [
            [(hm2s(17), False), (hm2s(20, 30), False), _('openen')],
			[(hm2s(20, 30), False), (hm2s(24), False), _('middelste dienst')],
            [(hm2s(24), False), (hm2s(28), True), _('sluiten')]],
		'cocks': [
            [(hm2s(17), True), (hm2s(20), False), _('Kok')]],
        'wok': [
            [(hm2s(17), True), (hm2s(20), False), _('WOKker')]]},
    'kleinfeest': {
        'tappers': [
            [(hm2s(20, 30), False), (hm2s(23), False), _('eerste dienst')],
            [(hm2s(23), False), (hm2s(25), False), _('tweede dienst')],
            [(hm2s(25), False), (hm2s(28), True), _('derde dienst')]],
        'sooscie': [
            [(hm2s(20, 30), False), (hm2s(24), False), _('openen')],
            [(hm2s(24), False), (hm2s(28), True), _('sluiten')]]},
    'grootfeest': {
        'tappers': [
            [(hm2s(20, 30), False), (hm2s(23), False),
                _('eerste dienst, tapper 1')],
            [(hm2s(20, 30), False), (hm2s(23), False),
                _('eerste dienst, tapper 2')],
            [(hm2s(23), False), (hm2s(25), False),
                _('tweede dienst, tapper 1')],
            [(hm2s(23), False), (hm2s(25), False),
                _('tweede dienst, tapper 2')],
            [(hm2s(25), False), (hm2s(28), True),
                _('derde dienst, tapper 1')],
            [(hm2s(25), False), (hm2s(28), True),
                _('derde dienst, tapper 2')]],
        'sooscie': [
            [(hm2s(19), False), (hm2s(24), False), _('openen')],
            [(hm2s(24), False), (hm2s(28), True), _('sluiten')]]},
    'dranktelling': {
        'sooscie': [
            [(hm2s(20), True), (hm2s(20, 30), False), _('Teller 1')],
            [(hm2s(20), True), (hm2s(20, 30), False), _('Teller 2')]]},
    'dranklevering': {
        'sooscie': [
            [(hm2s(9), False), (hm2s(13), False), _('Persoon 1')],
            [(hm2s(9), False), (hm2s(13), False), _('Persoon 2')]]},
    'vrijdag_met_tappers': {
        'tappers': [
            [(hm2s(20, 30), False), (hm2s(23), False), _('eerste dienst')],
            [(hm2s(23), False), (hm2s(25), False), _('tweede dienst')],
            [(hm2s(25), False), (hm2s(28), True), _('derde dienst')]],
        'sooscie': [
            [(hm2s(17), False), (hm2s(22), False), _('openen')],
            [(hm2s(22), False), (hm2s(27), True), _('sluiten')]],
        'cocks': [
            [(hm2s(16), True), (hm2s(19), False), _('Kok')]],
        'wok': [
            [(hm2s(16), True), (hm2s(19), False), _('Wokker')]]},
    'vrijdag_zonder_tappers': {
        'sooscie': [
            [(hm2s(17), False), (hm2s(22), False), _('openen')],
            [(hm2s(22), False), (hm2s(27), True), _('sluiten')]],
        'cocks': [
            [(hm2s(16), True), (hm2s(19), False), _('Kok')]],
        'wok': [
            [(hm2s(16), True), (hm2s(19), False), _('Wokker')]]},
    'koken': {
        'cocks': [
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 1')],
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 2')]]},
}



@login_required
def planning_view(request):
    period = 'now'
    if request.GET.get('year') in {'past1', 'past2'}:
        period = request.GET['year']
    pools = list(Pool.all())
    poolid2index = dict()
    poolids = set()
    for pool in pools:
        poolids.add(_id(pool))
    # TODO reduce number of queries
    current = date_to_midnight(now() - datetime.timedelta(days=1))
    past1year = date_to_midnight(now() - datetime.timedelta(days=356))
    past2year = date_to_midnight(now() - datetime.timedelta(days=356 * 2))
    if period == 'now':
        start = current
        end = None
    elif period == 'past1':
        start = past1year
        end = current
    elif period == 'past2':
        start = past2year
        end = past1year
    event_entities = list(Event.all_in_period(start, end))
    used_pools = set()
    for e in event_entities:
        for v in e.vacancies():
            used_pools.add(v.pool_id)
    pools_tpl = []
    i = 0
    for pool in pools:
        if _id(pool) not in used_pools:
            continue
        poolid2index[pool._id] = i
        pools_tpl.append(pool)
        i += 1
    events = list()
    for e in event_entities:
        ei = {'id': _id(e),
              'name': e.name,
              'datetime': e.date,
              'kind': e.kind,
              'vacancies': dict()}
        for index in poolid2index.values():
            ei['vacancies'][index] = list()
        for v in e.vacancies():
            ei['vacancies'][poolid2index[v.pool_id]].append({
                'begin': v.begin,
                'begin_time': v.begin_time,
                'end_time': v.end_time,
                'assignee': v.assignee.humanName
                if v.assignee else "?"})
        for index in poolid2index.values():
            ei['vacancies'][index].sort(key=lambda x: x['begin'])
        events.append(ei)
    events.sort(key=lambda x: x['datetime'])
    return render(request, 'planning/overview.html',
                  {'events': events,
                   'pools': pools_tpl,
                   'period': period})


@login_required
def planning_manage(request, poolname):
    if not may_manage_planning(request.user):
        raise PermissionDenied
    pool = Pool.by_name(poolname)
    if pool is None:
        raise Http404
    if not pool.may_manage(request.user):
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
            events[eid]['form'] = ManagePlanningForm(
                request.POST, pool=pool,
                vacancies=events[eid]['vacancies']
            )
            posted = True
        else:
            events[eid]['form'] = ManagePlanningForm(
                pool=pool,
                vacancies=events[eid]['vacancies']
            )
        if posted and events[eid]['form'].is_valid():
            for vacancy in events[eid]['vacancies']:
                worker = request.POST['shift_%s' % vacancy._id]
                if worker == '':
                    vacancy.assignee = None
                    vacancy.reminder_needed = True
                else:
                    if vacancy.assignee_id is None or \
                            _id(vacancy.assignee_id) != _id(worker):
                        delta = datetime.timedelta(days=5)
                        vacancy.reminder_needed = now() + delta < e.date
                        vacancy.assignee_id = _id(worker)
                vacancy.save()
    workers = pool.workers()
    # XXX het is cooler de shift dichtstbijzijnd aan de vacancy te
    # zoeken.  Stel dat iemand over een half-jaar al is ingepland
    # dan is dat niet zo boeiend.  Terwijl hij nu geen enkele
    # bardienst meer zou krijgen
    shifts = pool.last_shifts()
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
                scorers.sort(key=lambda x: shifts[_id(x)]
                             if shifts[_id(x)] else DT_MIN.date())
                for scorer in scorers:
                    vacancy.suggestions.append({
                        'scorer': scorer,
                        'score': score
                    })

    events = list(events.values())
    events.sort(key=lambda e: e['date'])
    return render(request, 'planning/manage.html',
                  {'events': events, 'pool': pool})


@login_required
def planning_poollist(request):
    if not may_manage_planning(request.user):
        # There's no planning you can change anyway, so what are you doing
        # here?
        raise PermissionDenied
    pools = list(Pool.all())
    return render(request, 'planning/pools.html',
                  {'pools': pools})


@login_required
def event_create(request):
    if not may_manage_planning(request.user):
        raise PermissionDenied
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
                        'end': (end_date, period[1][1]),
                        'pool': _id(pool),
                        'assignee': None,
                        'reminder_needed': True,
                    })
                    v.save()
            return HttpResponseRedirect(reverse('planning-event-edit',
                                                args=(e._id,)))
    else:
        form = EventCreateForm()
    return render(request, 'planning/event_create.html', {'form': form})


@login_required
def event_edit(request, eventid):
    if not may_manage_planning(request.user):
        raise PermissionDenied
    avform = None
    e = Event.by_id(eventid)
    if e is None:
        raise Http404
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
                (begin_hour, begin_minute) = map(int, fd['begin'].split(':'))
                (end_hour, end_minute) = map(int, fd['end'].split(':'))
                begin_offset = hm2s(begin_hour, begin_minute)
                end_offset = hm2s(end_hour, end_minute)
                begin_date = e.date + datetime.timedelta(seconds=begin_offset)
                end_date = e.date + datetime.timedelta(seconds=end_offset)
                v = Vacancy({
                    'name': fd['name'],
                    'event': _id(e),
                    'begin': (begin_date,
                              fd['begin_is_approximate'] == "True"),
                    'end': (end_date, fd['end_is_approximate'] == "True"),
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
        v.assignee_text = str(v.assignee.name) if v.assignee else "-"
        v.vid = str(v._id)
        vacancies.append(v)
    vacancies.sort(key=lambda x: str(x.pool_id) + str(x.begin))
    return render(
        request,
        'planning/event_edit.html',
        {'name': e.name, 'kind': e.kind, 'date': e.date.date(),
         'avform': avform, 'vacancies': vacancies},
    )


def _api_send_reminder(request):
    if not get_param(request, 'vacancy_id'):
        return JsonHttpResponse({'error': 'missing argument'})
    v = Vacancy.by_id(get_param(request, 'vacancy_id'))
    if not v:
        raise Http404
    if not v.pool.may_manage(request.user):
        raise PermissionDenied
    send_reminder(v, update=False)
    return JsonHttpResponse({'success': True})


@require_POST
@login_required
def planning_api(request):
    action = request.POST.get('action')
    if action == 'send-reminder':
        return _api_send_reminder(request)
    else:
        return JsonHttpResponse({'error': 'unknown action'})


@login_required
def planning_template(request, poolname):
    pool = Pool.by_name(poolname)
    events = list()
    # TODO reduce number of queries
    for e in Event.all_in_future():
        vacancies = list(e.vacancies(pool))
        if not vacancies:
            continue
        ei = {'name': e.name,
              'date': e.date,
              'vacancies': list()}
        shifts = dict()
        for v in vacancies:
            if v.begin not in shifts:
                shifts[v.begin] = {
                    'name': v.name,
                    'begin': v.begin,
                    'begin_time': v.begin_time,
                    'end_time': v.end_time,
                    'assignees': list()}
            shifts[v.begin]['assignees'].append(v.assignee)
        ei['vacancies'] = [x[1] for x
                           in sorted(shifts.items(), key=lambda x: x[0])]
        events.append(ei)
    events.sort(key=lambda x: x['date'])
    return render(request, 'planning/template.html', {'events': events})

# vim: et:sta:bs=2:sw=4:
