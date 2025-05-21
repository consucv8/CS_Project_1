from django.urls import path

from . import views

app_name = "exam"
urlpatterns = [
    path("", views.main, name="root"),
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("question_<int:question_id>/", views.question, name="question"),
    path("answer_<int:question_id>/", views.answer, name="answer"),
    path("answer_question_<int:question_id>/", views.answer_question, name="answer_question"),
    path("comment/", views.comment, name="comment"),
]
