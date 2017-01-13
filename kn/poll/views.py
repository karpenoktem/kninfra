import datetime

from django import forms
from django.http import Http404
from django.contrib import messages
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.forms.formsets import formset_factory
from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required

from kn.leden.mongo import _id

import kn.poll.entities as poll_Es

# We create for every answerSet a form


def create_questionForm(question):
    class QuestionForm(forms.Form):
        def __init__(self, *args, **kwargs):
            super(QuestionForm, self).__init__(*args, **kwargs)
            self.fields['answer'].label = question[0]
        answer = forms.ChoiceField(
                choices = list(enumerate(question[1])) + 
                        [(-1, _('(geen antwoord)'))],
                required=False)
    return QuestionForm


@login_required
def vote(request, name):
    poll = poll_Es.poll_by_name(name)
    if not poll:
        raise Http404
    filling = poll.filling_for(request.user)
    initial = False
    if not filling:
        initial = True
        filling = poll_Es.Filling({'user': _id(request.user),
                                   'poll': _id(poll),
                                   'answers': [None]*len(poll.questions)})
    allValid = True
    forms = [] # question forms
    for q_id, question in enumerate(poll.questions):
        form_kwargs = {'prefix': str(q_id)}
        answer = filling.answers[q_id]
        if answer is None:
            answer = -1
        form_kwargs['initial'] = {'answer': answer}
        if request.method == 'POST':
            form = create_questionForm(question)(request.POST, **form_kwargs)
            if not form.is_valid():
                allValid = False
        else:
            form = create_questionForm(question)(**form_kwargs)
        forms.append(form)
    if request.method == 'POST' and not poll.is_open:
        messages.error(request, _("De enquete is gesloten"))
    elif allValid and request.method == 'POST':
        messages.info(request, _("Veranderingen opgeslagen!"))
        for q_id, form in enumerate(forms):
            filling.answers[q_id] = int(form.cleaned_data['answer'])
        filling.date = datetime.datetime.now()
        filling.save()
    return render_to_response('poll/vote.html',
            {'forms': forms, 'poll': poll, 'initial': initial},
            context_instance=RequestContext(request))

# vim: et:sta:bs=2:sw=4:
