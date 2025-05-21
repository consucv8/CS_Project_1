from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseRedirect,
    HttpResponseBadRequest,
    HttpResponseForbidden,
)
from django.urls import reverse
from .models import Question, Comment, AnsweredQuestion, Answer
from django.views import generic
import sqlite3


def get_question(request):
    if "topic" in request.GET:
        topic = request.GET.get("topic")
        conn = sqlite3.connect("db.sqlite3")
        # Flaw: SQL Injection
        # FIX THE FIX
        # Fix (or use Question.objects.filter(topic=topic))
        # cursor.execute(
        #    "SELECT * FROM exam_question WHERE topic = ?",
        #    (topic,),
        #
        rows = (
            conn.cursor()
            .execute("SELECT id FROM exam_question WHERE topic LIKE '%" + topic + "%'")
            .fetchall()
        )
        ids = [row[0] for row in rows]
        topic = (
            conn.cursor()
            .execute(
                "SELECT topic FROM exam_question WHERE topic LIKE '%" + topic + "%'"
            )
            .fetchone()
        )
        if topic:
            topic = topic[0]
            questions = Question.objects.filter(id__in=ids)
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
    # Flaw: Students can access student dashboard
    # if not request.user.username == "teacher":
    #    return HttpResponseRedirect(reverse("exam:student_dashboard"))
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
        return HttpResponseRedirect(reverse("exam:teacher_dashboard"))
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
    ##If request.GET.answer
    question = get_object_or_404(Question, pk=question_id)
    if request.user.username == "teacher":
        return HttpResponseRedirect(reverse("exam:teacher_dashboard"))

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
    if request.method == "GET":
        selected_answer = request.GET.get("answer")
        answer = question.answers.get(id=selected_answer)
        if selected_answer in AnsweredQuestion.objects.filter(
            student=request.user.student
        ).values_list("answer_id", flat=True):
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
        return HttpResponseForbidden("Invalid request method.")


@login_required
def comment(request):
    if request.method == "POST":
        title = request.POST.get("title")
        comment_text = request.POST.get("comment_text")
        comment = Comment(user=request.user, comment_text=comment_text, title=title)
        comment.save()
        return HttpResponseRedirect(reverse("exam:student_dashboard"))
    else:
        return HttpResponseForbidden("Invalid request method.")


@login_required
def main(request):
    if request.user.username == "teacher":
        return HttpResponseRedirect(reverse("exam:teacher_dashboard"))
    else:
        return HttpResponseRedirect(reverse("exam:student_dashboard"))
