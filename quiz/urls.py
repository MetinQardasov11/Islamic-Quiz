from django.urls import path

from . import views

app_name = 'quiz'

urlpatterns = [
    path('quizzes/', views.quizzes, name='quizzes'),
    path('quiz/', views.quiz, name='quiz'),
    path('result/', views.result, name='result'),
    path('review/', views.review, name='review'),
    path('multiplayer/', views.multiplayer, name='multiplayer'),
    path('api/quizzes/', views.quizzes_api, name='quizzes_api'),
    path('api/attempts/submit/', views.submit_quiz_attempt, name='submit_quiz_attempt'),
    path('api/attempts/<int:attempt_id>/', views.quiz_attempt_detail, name='quiz_attempt_detail'),
    path('api/multiplayer/save/', views.save_multiplayer_session, name='save_multiplayer_session'),
]
