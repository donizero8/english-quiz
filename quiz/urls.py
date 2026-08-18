from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("quiz/<slug:slug>/", views.quiz_detail, name="quiz-detail"),
    path("quiz/<slug:slug>/submit/", views.submit_quiz, name="submit-quiz"),
    path("api/conversations/<int:pk>/generate-audio/", views.generate_conversation_audio, name="generate-audio"),
]
