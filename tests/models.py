from pyrestcli.fields import CharField, IntegerField, DateTimeField, ResourceField
from pyrestcli.resources import Resource, Manager


class QuestionField(ResourceField):
    value_class = "models.Question"


class ChoiceField(ResourceField):
    value_class = "models.Choice"


class Question(Resource):
    id = IntegerField()
    question_text = CharField()
    pub_date = DateTimeField()
    choices = ChoiceField(many=True)

    class Meta:
        name_field = "question_text"


class Choice(Resource):
    id = IntegerField()
    question = QuestionField()
    choice_text = CharField()
    votes = IntegerField()

    class Meta:
        name_field = "choice_text"


class QuestionManager(Manager):
    resource_class = Question
    json_collection_attribute = "results"


class ChoiceManager(Manager):
    resource_class = Choice
    json_collection_attribute = "results"
