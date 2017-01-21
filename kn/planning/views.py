from random import shuffle

import datetime

from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http  import require_POST

from kn.base.http import JsonHttpResponse
from kn.leden.date import date_to_dt, now, date_to_midnight
from kn.leden.mongo import _id

from kn.planning.entities import Pool, Event, Vacancy, may_manage_planning
from kn.planning.score import planning_vacancy_worker_score
from kn.planning.utils import send_reminder
from kn.planning.forms import ManagePlanningForm, AddVacancyForm, EventCreateForm


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
            [(hm2s(24), False), (hm2s(28), True), _('sluiten')]],
        'draai': [
            [(hm2s(20, 45), False), (hm2s(23), False), _('openen')],
            [(hm2s(23), False), (hm2s(24), False), _('prime-time')],
            [(hm2s(24), False), (hm2s(25), True), _('sluiten')]]},
    'kleinfeest': {
        'tappers': [
            [(hm2s(20, 30), False), (hm2s(23), False), _('eerste dienst')],
            [(hm2s(23), False), (hm2s(25), False), _('tweede dienst')],
            [(hm2s(25), False), (hm2s(28), True), _('derde dienst')]],
        'bestuur': [
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
        'bestuur': [
            [(hm2s(20, 30), False), (hm2s(24), False), _('openen')],
            [(hm2s(24), False), (hm2s(28), True), _('sluiten')]]},
    'dranktelling': {
        'barco': [
            [(hm2s(20), True), (hm2s(20, 30), False), _('Teller 1')],
            [(hm2s(20), True), (hm2s(20, 30), False), _('Teller 2')]]},
    'dranklevering': {
        'barco': [
            [(hm2s(9), False), (hm2s(13), False), _('Persoon 1')],
            [(hm2s(9), False), (hm2s(13), False), _('Persoon 2')]]},
    'vrijdag_met_tappers': {
        'tappers': [
            [(hm2s(20, 30), False), (hm2s(23), False), _('eerste dienst')],
            [(hm2s(23), False), (hm2s(25), False), _('tweede dienst')],
            [(hm2s(25), False), (hm2s(28), True), _('derde dienst')]],
        'bestuur': [
            [(hm2s(17), False), (hm2s(22), False), _('openen')],
            [(hm2s(22), False), (hm2s(27), True), _('sluiten')]],
        'cocks': [
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 1')],
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 2')]]},
    'vrijdag_zonder_tappers': {
        'bestuur': [
            [(hm2s(17), False), (hm2s(22), False), _('openen')],
            [(hm2s(22), False), (hm2s(27), True), _('sluiten')]],
        'cocks': [
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 1')],
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 2')]]},
    'koken': {
        'cocks': [
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 1')],
            [(hm2s(17), True), (hm2s(19, 30), False), _('Kok 2')]]},
}


@login_required
def planning_view(request):
    if 'lookbehind' in request.GET:
        lookbehind = int(request.GET['lookbehind'])
    else:
        lookbehind = 1
    pools = list(Pool.all())
    poolid2index = dict()
    poolids = set()
    for pool in pools:
        poolids.add(_id(pool))
    # TODO reduce number of queries
    event_entities = list(Event.all_since_datetime(
        date_to_midnight(now()) - datetime.timedelta(days=lookbehind)))
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
    return render_to_response('planning/overview.html',
                              {'events': events,
                               'pools': pools_tpl},
                              context_instance=RequestContext(request))

# extends cmp with None as bottom


def cmp_None(x, y, cmp=cmp):
    if x is None:
        return -1
    if y is None:
        return 1
    return cmp(x, y)


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
                scorers.sort(key=lambda x: shifts[_id(x)], cmp=cmp_None)
                for scorer in scorers:
                    vacancy.suggestions.append({
                        'scorer': scorer,
                        'score': score
                    })

    events = list(events.values())
    events.sort(key=lambda e: e['date'])
    return render_to_response('planning/manage.html',
                              {'events': events, 'pool': pool},
                              context_instance=RequestContext(request))


@login_required
def planning_poollist(request):
    if not may_manage_planning(request.user):
        # There's no planning you can change anyway, so what are you doing here?
        raise PermissionDenied
    pools = list(Pool.all())
    return render_to_response('planning/pools.html',
                              {'pools': pools},
                              context_instance=RequestContext(request))


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
    return render_to_response('planning/event_create.html', {'form': form},
                              context_instance=RequestContext(request))


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
                    'begin': (begin_date, fd['begin_is_approximate'] == "True"),
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
    return render_to_response(
        'planning/event_edit.html',
        {'name': e.name, 'kind': e.kind, 'date': e.date.date(),
         'avform': avform, 'vacancies': vacancies},
         context_instance=RequestContext(request)
    )


def _api_send_reminder(request):
    if 'vacancy_id' not in request.REQUEST:
        return JsonHttpResponse({'error': 'missing argument'})
    v = Vacancy.by_id(request.REQUEST['vacancy_id'])
    if not v:
        raise Http404
    if not v.pool.may_manage(request.user):
        raise PermissionDenied
    send_reminder(v, update=False)
    return JsonHttpResponse({'success': True})


@require_POST
@login_required
def planning_api(request):
    action = request.REQUEST.get('action')
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
        ei['vacancies'] = map(lambda x: x[1], sorted(shifts.items(),
                                                     key=lambda x: x[0]))
        events.append(ei)
    events.sort(key=lambda x: x['date'])
    return render_to_response('planning/template.html', {'events': events},
                              context_instance=RequestContext(request))

# vim: et:sta:bs=2:sw=4:
