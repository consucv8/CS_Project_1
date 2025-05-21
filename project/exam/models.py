from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class Question(models.Model):
    topic = models.CharField(max_length=50)
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text


class Answer(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="answers"
    )
    answer_text = models.CharField(max_length=200)
    correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer_text + " (Correct)" if self.correct else ""


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    grade = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + " (Grade: " + str(self.grade) + ")"


class AnsweredQuestion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.user.username} - {self.question.question_text} : {self.answer.answer_text}"


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    title = models.CharField(max_length=200)
    comment_text = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
