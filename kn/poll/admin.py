from models import Poll, AnswerSet, Answer, Question, Filling
from django.contrib import admin

for m in (Poll, AnswerSet, Answer, Question):
	admin.site.register(m)
