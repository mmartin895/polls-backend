from django.contrib import admin
from .models import Poll, Question, Answer, CustomUser, FavoritePoll

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

class FavoritePollAdmin(admin.ModelAdmin):
    fieldsets = None
    list_display = ('user', 'poll')    

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Poll, PollAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)
admin.site.register(FavoritePoll, FavoritePollAdmin)