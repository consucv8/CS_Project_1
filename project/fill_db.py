import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
django.setup()


from exam.models import Question, Answer, Student
from django.contrib.auth.models import User
import csv

with open("questions.csv", "r") as questions_file:
    with open("answers.csv", "r") as answers_file:
        questions_reader = csv.DictReader(questions_file)
        answers_reader = csv.DictReader(answers_file)
        for q in questions_reader:
            question = Question(question_text=q["text"], topic=q["topic"])
            question.save()
            for i in range(4):
                a = next(answers_reader)
                answer = Answer(
                    question=question,
                    answer_text=a["text"],
                    correct=bool(int(a["correct"])),
                )
                answer.save()

with open("users.csv", "r") as users_file:
    users_reader = csv.DictReader(users_file)
    for u in users_reader:
        user = User(username=u["username"])
        user.set_password(u["password"])
        user.save()
        if u["username"] != "teacher":
            student = Student(user=user)
            student.save()
