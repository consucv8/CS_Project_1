from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
)
from django.urls import reverse
from .models import Question, Comment, AnsweredQuestion
import sqlite3


def get_question(request):
    if "topic" in request.GET:
        topic = request.GET.get("topic")
        conn = sqlite3.connect("db.sqlite3")
        # Flaw: SQL Injection
        topic = (
            conn.cursor()
            .execute(
                "SELECT topic FROM exam_question WHERE topic LIKE '%" + topic + "%'"
            )
            .fetchone()
        )
        # Fix: Use parameterized queries
        # topic = (
        #    conn.cursor()
        #    .execute(
        #        "SELECT topic FROM exam_question WHERE topic LIKE ?", (f"%{topic}%",)
        #    )
        #    .fetchone()
        # )
        if topic:
            topic = topic[0]
            questions = Question.objects.filter(topic=topic)
        else:
            topic = "All Topics"
            questions = Question.objects.all()
        conn.close()
    else:
        questions = Question.objects.all()
        topic = "All Topics"
    return questions, topic


@login_required
def teacher_dashboard(request):
    # Flaw: Students can access teacher dashboard
    # Fix: Check if user is teacher
    # if request.user.username != "teacher":
    #    return HttpResponseForbidden("You are not allowed to view this page.")
    questions, topic = get_question(request)
    question_url = "/exam/answer_"
    comments = Comment.objects.all()
    return render(
        request,
        "exam/teacher_dashboard.html",
        {
            "questions": questions,
            "topic": topic,
            "comments": comments,
            "base_url": question_url,
        },
    )


@login_required
def student_dashboard(request):
    if request.user.username == "teacher":
        return HttpResponseForbidden("You are not allowed to view this page.")
    questions, topic = get_question(request)
    question_url = "/exam/question_"
    student = request.user.student
    return render(
        request,
        "exam/student_dashboard.html",
        {
            "questions": questions,
            "topic": topic,
            "base_url": question_url,
            "student": student,
        },
    )


@login_required
def question(request, question_id):
    if request.user.username == "teacher":
        return HttpResponseForbidden("You are not allowed to view this page.")
    question = get_object_or_404(Question, pk=question_id)
    if question_id in AnsweredQuestion.objects.filter(
        student=request.user.student
    ).values_list("question_id", flat=True):
        answer = AnsweredQuestion.objects.get(
            student=request.user.student, question=question
        ).answer
        return render(
            request,
            "exam/answered_question.html",
            {"question": question, "selected_answer": answer, "readonly": True},
        )

    return render(
        request,
        "exam/answer_question.html",
        {
            "question": question,
        },
    )


@login_required
def answer(request, question_id):
    # Flaw: Students can access teacher answers
    # Fix: Check if user is teacher
    # if request.user.username != "teacher":
    #    return HttpResponseForbidden("You are not allowed to view this page.")
    question = get_object_or_404(Question, pk=question_id)
    answer = question.answers.get(correct=True)
    return render(
        request,
        "exam/correct_answer.html",
        {
            "question": question,
            "correct_answer": answer,
            "readonly": True,
        },
    )


@login_required
def answer_question(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    if request.user.username == "teacher":
        return HttpResponseForbidden("You are not allowed to view this page.")
    # Flaw: Get allows avoidance of CSRF
    # Fix: Use POST. for which django checks CSRF token
    # if request.method == "POST":
    if request.method == "GET":
        # selected_answer = request.POST.get("answer")
        selected_answer = request.GET.get("answer")
        answer = question.answers.get(id=selected_answer)
        if question_id in AnsweredQuestion.objects.filter(
            student=request.user.student
        ).values_list("question_id", flat=True):
            return HttpResponseBadRequest("You have already answered this question.")
        answered_question = AnsweredQuestion(
            student=request.user.student, question=question, answer=answer
        )
        answered_question.save()
        if answer.correct:
            request.user.student.grade += 1
            request.user.student.save()
        return HttpResponseRedirect(reverse("exam:question", args=(question_id,)))
    else:
        return HttpResponseNotAllowed(["GET"])
        # return HttpResponseNotAllowed(["POST"])


@login_required
def comment(request):
    if request.user.username == "teacher":
        return HttpResponseForbidden("You are not allowed to view this page.")
    if request.method == "POST":
        title = request.POST.get("title")
        comment_text = request.POST.get("comment_text")
        comment = Comment(user=request.user, comment_text=comment_text, title=title)
        comment.save()
        return HttpResponseRedirect(reverse("exam:student_dashboard"))
    else:
        return HttpResponseNotAllowed(["POST"])


@login_required
def main(request):
    if request.user.username == "teacher":
        return HttpResponseRedirect(reverse("exam:teacher_dashboard"))
    else:
        return HttpResponseRedirect(reverse("exam:student_dashboard"))
