from rest_framework import serializers

from polls.models import Question, Choice


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
