# vim: et:sta:bs=2:sw=4:
from django.http import Http404
from django import forms
from django.template import RequestContext
from kn.poll.models import Filling, Answer, AnswerSet, Poll, Question
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory

# We create for every answerSet a form
def create_questionForm(_as):
    class QuestionForm(forms.Form):
        def __init__(self, q, *args, **kwargs):
            super(QuestionForm, self).__init__(*args, **kwargs)
            self.fields['answer'].label = q.text
        answer = forms.ModelChoiceField(
                queryset = _as.answer_set.order_by(
                        'text').all(),
                required=False)
    return QuestionForm

@login_required
def vote(request, name):
    try:
        poll = Poll.objects.select_related(
                'question_set__answers').get(name=name)
    except Poll.DoesNotExist:
        raise Http404
    as_lut = dict()
    qfs = list()
    questions = list()
    allValid = True
    f_lut = dict()
    fillings = list(Filling.objects.filter(user=request.user,
                           question__poll=poll))
    for fi in fillings:
        f_lut[fi.question.pk] = fi
    for q in poll.question_set.all():
        if not q.answers.pk in as_lut:
            as_lut[q.answers.pk] = create_questionForm(
                            q.answers)
        form_kwargs = {'prefix': q.pk}
        if q.pk in f_lut:
            form_kwargs['initial'] = {
                    'answer': f_lut[q.pk].answer_id}
        if request.method == 'POST':
            form = as_lut[q.answers.pk](q,
                            request.POST,
                            **form_kwargs)
            if not form.is_valid():
                allValid = False
        else:
            form = as_lut[q.answers.pk](q,
                            **form_kwargs)
        qfs.append((q, form))
    if request.method == 'POST' and not poll.isOpen:
        request.user.push_message("De enquete is gesloten")
    elif allValid and request.method == 'POST':
        request.user.push_message('Veranderingen opgeslagen!')
        for fi in fillings:
            fi.delete()
        for q, form in qfs:
            answer = form.cleaned_data['answer']
            if answer is None:
                continue
            Filling.objects.create(user=request.user,
                           answer=answer,
                           question=q)
    return render_to_response('poll/vote.html',
            {'forms': map(lambda x: x[1], qfs),
             'poll': poll},
            context_instance=RequestContext(request))
