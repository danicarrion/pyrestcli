from __future__ import unicode_literals

from django.db import migrations
from django.contrib.auth.hashers import make_password
from django.utils import timezone


def create_test_models(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Question = apps.get_model("polls", "Question")
    Choice = apps.get_model("polls", "Choice")

    user = User(username="admin", email="admin@admin.com")
    user.password = make_password('admin')
    user.save()

    question_1 = Question(question_text="Do you like pizza?", pub_date=timezone.now())
    question_1.save()

    choice_1_1 = Choice(question=question_1, choice_text="Yes", votes=5)
    choice_1_1.save()
    choice_1_2 = Choice(question=question_1, choice_text="No", votes=2)
    choice_1_2.save()

    question_2 = Question(question_text="Do you like spaguetti?", pub_date=timezone.now())
    question_2.save()

    choice_2_1 = Choice(question=question_2, choice_text="Yes", votes=7)
    choice_2_1.save()
    choice_2_2 = Choice(question=question_2, choice_text="Yes", votes=4)
    choice_2_2.save()


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_test_models),
    ]
