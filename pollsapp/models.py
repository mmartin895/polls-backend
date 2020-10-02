from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
import datetime
from django.http import Http404

class CustomUser(AbstractUser):
    def __str__(self):
        return self.username

class PollManager(models.Manager):
    def archive(self, pk, user):
        poll = self.get(pk=pk,user=user)
        poll.archived = True
        poll.archived_at = datetime.datetime.now()
        poll.save()

    def restore(self, pk):
        poll = self.get(pk=pk,archived=True)
        poll.archived = False
        poll.archived_at = None
        poll.save()

     

class Poll(models.Model):
    class Meta:
        permissions = [
            ('archived_polls_administration', 'Can manage archived polls')
        ]

    title = models.CharField(max_length=50)
    description = models.CharField(max_length=100, blank=True)
    archived = models.BooleanField(default=False)
    premium = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    archived_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='polls', on_delete=models.CASCADE)

    @property
    def isFavorite(self):
        if not (hasattr(self, '_isFavorite')):
            self._isFavorite = False
        return self._isFavorite


    @isFavorite.setter
    def isFavorite(self, value):
        self._isFavorite = value

    objects = PollManager()
    


class Question(models.Model):
    class QuestionChoice(models.TextChoices):
        TEXT_INPUT = 'TI', _('Text Input')
        NUMERIC_INPUT = 'NI', _('Numeric Input')
        SINGLE_CHOICE = 'SC', _('Single Choice')
        MULTIPLE_CHOICE = 'MC', _('Multiple Choice')
        DROPDOWN_CHOICE = 'DC', _('Dropdown Choice')

    content = models.CharField(max_length=100)
    choices = models.CharField(max_length=200, blank=True)
    required = models.BooleanField(default=False)
    type = models.CharField(max_length=2, choices=QuestionChoice.choices, default=QuestionChoice.TEXT_INPUT)
    poll = models.ForeignKey(Poll, related_name='questions', on_delete=models.CASCADE)

    def __str__(self):
        return self.content


class SubmittedPoll(models.Model):
    answered_at = models.DateTimeField(auto_now_add=True)
    poll = models.ForeignKey(Poll, related_name='submitted_polls', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='submitted_polls', on_delete=models.CASCADE, blank=True, null=True)


class Answer(models.Model):
    answer = models.CharField(max_length=100, blank=True, null=True)
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    submitted_poll = models.ForeignKey(SubmittedPoll, related_name='answers', on_delete=models.CASCADE)

    def __str__(self):
        return self.answer

class FavoritePoll(models.Model):
    poll = models.ForeignKey(Poll, related_name='poll', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user', on_delete=models.CASCADE, blank=True, null=True)