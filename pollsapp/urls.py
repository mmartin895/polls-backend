from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'polls', views.PollViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'submitted-polls', views.SubmittedPollViewSet)
router.register(r'answers', views.AnswerViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('users/', views.UserListView.as_view()),
    path('auth/', include('rest_auth.urls')),
    path('auth/registration/', include('rest_auth.registration.urls')),
]