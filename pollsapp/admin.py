from django.contrib import admin
from .models import Poll, Question, Answer, CustomUser

class UserAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ('id', 'username', 'email')

class PollAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ('title', 'description', 'created_at', 'archived', 'archived_at')

class QuestionAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ('content', 'type', 'poll', 'required')

class AnswerAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ('answer', 'submitted_poll', 'question')

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)