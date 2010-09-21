from models import Poll, AnswerSet, Answer, Question, Filling
from django.contrib import admin

class AnswerAdmin(admin.ModelAdmin):
	list_filter = ('answerSet',)

class QuestionAdmin(admin.ModelAdmin):
	list_filter = ('poll',)

admin.site.register(Poll)
admin.site.register(AnswerSet)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(Question, QuestionAdmin)
