import collections

from rest_framework import serializers
from .models import Poll, Question, Answer, CustomUser, SubmittedPoll, FavoritePoll
from django.conf import settings
from rest_auth.models import TokenModel
from rest_auth.utils import import_callable
# from rest_auth.serializers import UserDetailsSerializer as DefaultUserDetailsSerializer

import logging
from django.contrib.auth.models import Permission

logger = logging.getLogger("mylogger")
logger.info("Whatever to log")


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'polls',)

class CustomPermissionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('id', 'codename')

class CustomUserDetailsSerializer(serializers.ModelSerializer):

    user_permissions = CustomPermissionsSerializer(many=True)
    """
    User model w/o password
    """
    class Meta:
        model = CustomUser
        fields = ('pk', 'username', 'email', 'first_name', 'last_name', 'user_permissions')
        read_only_fields = ('email', 'user_permissions')


# This is to allow you to override the UserDetailsSerializer at any time.
# If you're sure you won't, you can skip this and use DefaultUserDetailsSerializer directly
rest_auth_serializers = getattr(settings, 'REST_AUTH_SERIALIZERS', {})
UserDetailsSerializer = import_callable(
    rest_auth_serializers.get('USER_DETAILS_SERIALIZER', CustomUserDetailsSerializer)
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
        fields = ['id', 'title', 'description', 'archived', 'premium', 'archived_at', 'created_at', 'questions', 'user','isFavorite']
        read_only_fields = ('id', 'created_at', 'archived_at', 'user')

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
        read_only_fields = ('id',)        
