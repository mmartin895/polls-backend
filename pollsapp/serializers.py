import collections

from rest_framework import serializers
from .models import Poll, Question, Answer, CustomUser, SubmittedPoll, FavoritePoll
from django.conf import settings
from rest_auth.models import TokenModel
from rest_auth.utils import import_callable
from rest_auth.serializers import UserDetailsSerializer as DefaultUserDetailsSerializer

import logging

logger = logging.getLogger("mylogger")
logger.info("Whatever to log")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'polls',)


# This is to allow you to override the UserDetailsSerializer at any time.
# If you're sure you won't, you can skip this and use DefaultUserDetailsSerializer directly
rest_auth_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})
UserDetailsSerializer = import_callable(
    rest_auth_serializers.get('USER_DETAILS_SERIALIZER', DefaultUserDetailsSerializer)
)


class CustomTokenSerializer(serializers.ModelSerializer):
    user = UserDetailsSerializer(read_only=True)

    class Meta:
        model = TokenModel
        fields = ('key', 'user')


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(model_field=Question()._meta.get_field('id'))

    class Meta:
        model = Question
        fields = ['id', 'content', 'choices', 'type', 'required', 'answers']
        read_only_fields = ('answers', 'id',)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'answer', 'question']
        read_only_fields = ('id',)


class PollSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    questions = QuestionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ['id', 'title', 'description', 'archived', 'premium', 'archived_at', 'created_at', 'questions', 'user']
        read_only_fields = ('id', 'created_at', 'archived_at', 'user',)

    def create(self, validated_data):
        questions_data = validated_data.pop('questions')
        poll = Poll.objects.create(**validated_data)
        for question in questions_data:
            del question['id']
            Question.objects.create(poll=poll, **question)
        return poll

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions')
        questions_data = list(questions_data)
        logger.info(questions_data)
        questions = (instance.questions).all()
        questions = list(questions)  # pitanja u bazi

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.premium = validated_data.get('premium', instance.premium)
        instance.save()
        questions_to_delete = []

        # questions - pitanja iz baze
        # questions_data - pitanja iz requesta

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


class SubmittedPollSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    answers = AnswerSerializer(many=True)

    class Meta:
        model = SubmittedPoll
        fields = ['id', 'answered_at', 'poll', 'answers', 'user']
        read_only_fields = ('id', 'answered_at', 'user',)

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        submitted_poll = SubmittedPoll.objects.create(**validated_data)
        for answer in answers_data:
            Answer.objects.create(submitted_poll=submitted_poll, **answer)
        return submitted_poll

class FavoritePollSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.email')
    poll = serializers.ReadOnlyField(source='poll.id')

    class Meta:
        model = FavoritePoll
        fields = ['id', 'poll', 'user']
        read_only_fields = ('id', 'poll', 'user',)        
