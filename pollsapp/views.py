from rest_framework import viewsets
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import PollSerializer, QuestionSerializer, SubmittedPollSerializer, AnswerSerializer, UserSerializer, FavoritePollSerializer
from .models import Poll, Question, SubmittedPoll, Answer, CustomUser, FavoritePoll
from django.http import HttpResponseForbidden


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    filterset_fields = ('user',)
    permission_classes_by_action = {'create': [IsAuthenticated]}    

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def archive(self, request, pk=None):
        poll = self.get_object()
        poll.setArchived(True)
        poll.save()
        return Response({'status': 'archived set'})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        user = self.request.user
        polls = Poll.objects.filter(favoritepoll__user__user_id=user.id).distinct()
        serializer = PollSerializer(polls, many=True)     
        return Response(serializer.data)   

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return Poll.objects.filter(archived=False)

    def get_permissions(self):
        try:
            # return permission_classes depending on `action` 
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError: 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]        
        

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

class FavoritePollViewSet(viewsets.ModelViewSet):
    queryset = FavoritePoll.objects.all()
    serializer_class = FavoritePollSerializer
    permission_classes = (IsAuthenticated,) 

    def get_queryset(self):
        queryset = FavoritePoll.objects.filter(user=self.request.user) 
        return queryset