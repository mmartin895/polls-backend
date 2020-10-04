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
    def get_queryset(self):
        return super().get_queryset().filter(archived=False)

    def get_archived(self):
        return super().get_queryset().filter(archived=True)

    def get_favorites(self,user):
        favorites = list(FavoritePoll.objects
            .filter(user_id=user.id)
            .select_related('poll'))
            
        result_list = list()
        for fp in favorites:
            fp.poll.isFavorite=True
            if not (fp.poll.archived):
                result_list.append(fp.poll)
        return result_list        


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

    def create(self, user, validated_data):
        questions_data = validated_data.pop('questions')
        poll = super().create(**validated_data,user=user)
        for question in questions_data:
            del question['id']
            Question.objects.create(poll=poll, **question)

        return poll

    def update(self, instance, validated_data):
        questions_data = list(validated_data.pop('questions')) # pitanja iz requesta
        questions = list(instance.questions.all()) # pitanja u bazi

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.premium = validated_data.get('premium', instance.premium)
        instance.save()
        questions_to_delete = []

        for q_instance in questions:
            found_question = next((q for q in questions_data if q.get('id') == q_instance.id), None)
            if found_question:
                # pitanje postoji->update pitanja u bazi
                # brisanje pitanja iz requesta kako bi ostala samo pitanja koja treba dodati
                q_instance.content = found_question.get('content', q_instance.content)
                q_instance.type = found_question.get('type', q_instance.type)
                q_instance.choices = found_question.get('choices', q_instance.choices)
                q_instance.required = found_question.get('required', q_instance.required)
                q_instance.save()
                questions_data.remove(found_question)

            else:
                # dodajemo q_instance u questions to delete
                questions_to_delete.append(q_instance)

        for q in questions_data:
            del q['id']
            Question.objects.create(poll=instance, **q)

        for q in questions_to_delete:
            q.delete()

        return instance        
     

class Poll(models.Model):
    class Meta:
        permissions = [
            ('archived_polls_administration', 'Can manage archived polls')
        ]

    objects = PollManager()

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