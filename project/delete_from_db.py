import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
django.setup()

from exam.models import *
from django.contrib.auth.models import User

Student.objects.all().delete()
Question.objects.all().delete()
Answer.objects.all().delete()
Comment.objects.all().delete()
AnsweredQuestion.objects.all().delete()
User.objects.all().delete()
