from rest_framework import viewsets
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission

from .serializers import PollSerializer, QuestionSerializer, SubmittedPollSerializer, AnswerSerializer, UserSerializer, FavoritePollSerializer
from .models import Poll, Question, SubmittedPoll, Answer, CustomUser, FavoritePoll
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404


class UserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class IsPollAdministrator(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and 
        request.user.is_authenticated and 
        request.user.has_perm('pollsapp.archived_polls_administration'))

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    filterset_fields = ('user',)
    permission_classes_by_action = {'create': [IsAuthenticated]}    

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def archive(self, request, pk=None):
        Poll.objects.archive(self.kwargs['pk'], self.request.user)
        return Response({'status': 'archived set'})

    @action(detail=True, methods=['post'], permission_classes=[IsPollAdministrator])
    def restore(self, request, pk=None):
        Poll.objects.restore(self.kwargs['pk'])
        return Response({'status': 'poll {id} successfully restored'.format(self.kwargs['pk'])})        

    @action(detail=False, methods=['get'], permission_classes=[IsPollAdministrator])
    def archived(self, request):
        polls = list(Poll.objects.filter(archived=True))
        if (request.user.is_authenticated):
            self.setIsFavorite(polls)

        serializer = self.get_serializer(polls, many=True)
        return Response(serializer.data)      

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def favorites(self, request):
        user = self.request.user
        favorites = list(FavoritePoll.objects
            .filter(user_id=user.id)
            .select_related('poll'))
            
        favoritePolls = list()
        for fp in favorites:
            fp.poll.isFavorite=True
            if not (fp.poll.archived):
                favoritePolls.append(fp.poll)
        
        serializer = PollSerializer(favoritePolls, many=True)     
        return Response(serializer.data)   

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if (request.user.is_authenticated):
            favorites = list(FavoritePoll.objects.filter(user_id = self.request.user.id))
            instance.isFavorite = next((fav for fav in favorites if fav.poll_id == instance.id), None) is not None

        serializer = self.get_serializer(instance)
        return Response(serializer.data)        

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        polls = list(queryset)

        # TODO: Introduce pagination at later point
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     polls = list(page)
        #     serializer = self.get_serializer(polls, many=True)
        #     if (request.user.is_authenticated):
        #         self.setIsFavorite(serializer)

        #     return self.get_paginated_response(serializer.data)

        
        if (request.user.is_authenticated):
            self.setIsFavorite(polls)

        serializer = self.get_serializer(polls, many=True)
        return Response(serializer.data)

    def setIsFavorite(self, polls):
        favorites = list(FavoritePoll.objects.filter(user_id = self.request.user.id))

        for poll in polls:
            favorite = next((fav for fav in favorites if fav.poll_id == poll.id), None)
            poll.isFavorite = favorite is not None
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if not (instance.user==self.request.user):
            return Response({'status': 'unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        self.perform_update(serializer)
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
    permission_classes = (IsAdminUser,) 
    permission_classes_by_action = {'create': [IsAuthenticated],
                                    'destroy' : [IsAuthenticated]}


    def perform_create(self, serializer):
        user=self.request.user
        poll = Poll.objects.get(pk=self.request.data['poll'])
        if not (FavoritePoll.objects.filter(user_id=user.id,poll_id=poll.id).exists()):
            favoritePoll = FavoritePoll()
            favoritePoll.user = user
            favoritePoll.poll = poll
            favoritePoll.save()

    def destroy(self, request, *args, **kwargs):
        user=self.request.user
        instance = get_object_or_404(FavoritePoll.objects.filter(user_id=user.id,poll_id=kwargs['pk']))
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)            
       

    def get_permissions(self):
        try:
            # return permission_classes depending on `action` 
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError: 
            # action is not set return default permission_classes
            return [permission() for permission in self.permission_classes]            