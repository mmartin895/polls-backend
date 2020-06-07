from rest_framework import serializers
from .models import Poll, Question, Answer, CustomUser, SubmittedPoll
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
    class Meta:
        model = Question
        fields = ['id', 'content', 'choices', 'type', 'required', 'answers']
        read_only_fields = ('id', 'answers',)


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
            Question.objects.create(poll=poll, **question)
        return poll

    def update(self, instance, validated_data):
        questions_data = validated_data.pop('questions')
        logger.info(questions_data)
        questions = (instance.questions).all()
        questions = list(questions)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.premium = validated_data.get('premium', instance.premium)
        instance.save()

        # questions - pitanja iz baze
        # questions_data - pitanja iz requesta
        i = 0
        for q_instance in questions:
            q_data = questions_data[i]
            logger.info(q_instance.id)
            logger.info(q_data)
            # if q_instance.id == q_data.get('id'):
            q_instance.content = q_data.get('content', q_instance.content)
            q_instance.type = q_data.get('type', q_instance.type)
            q_instance.choices = q_data.get('choices', q_instance.choices)
            q_instance.required = q_data.get('required', q_instance.required)
            q_instance.save()
            # else:
            #     q_instance.delete()
            i += 1

        while i < len(questions_data):
            Question.objects.create(poll=instance, **questions_data[i])
            i += 1

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
