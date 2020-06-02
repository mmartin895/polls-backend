from rest_framework import viewsets
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import PollSerializer, QuestionSerializer, SubmittedPollSerializer, AnswerSerializer, UserSerializer
from .models import Poll, Question, SubmittedPoll, Answer, CustomUser

class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    filterset_fields = ('user',)

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        poll = self.get_object()
        poll.setArchived(True)
        poll.save()
        return Response({'status': 'archived set'})

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Poll.objects.filter(archived=False)


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_queryset(self):
        queryset = Question.objects.all()
        poll = self.request.query_params.get('poll', None)
        if poll is not None:
            queryset = queryset.filter(poll=poll)
        return queryset


class SubmittedPollViewSet(viewsets.ModelViewSet):
    queryset = SubmittedPoll.objects.all()
    serializer_class = SubmittedPollSerializer
    filterset_fields = ('poll',)

    def perform_create(self, serializer):
        user = self.request.user
        if user.id:
            serializer.save(user=self.request.user)
        else:
            serializer.save()


class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
