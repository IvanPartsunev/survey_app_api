from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.response import Response

from polls_app.core.models import QuestionModel, ChoiceModel, CommentModel, ProductModel
from polls_app.custom_exeption import ApplicationError


class AnswerSerializer(serializers.ModelSerializer):
    """
    If no pk is provided, a new answer will be created.
    """
    pk = serializers.IntegerField(required=False)

    class Meta:
        model = ChoiceModel
        fields = [
            "pk",
            "choice_text",
            "votes",
            "created_on",
            "edited_on",
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = [
            "comment",
            "created_on",
            "edited_on",
        ]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, source="question_choices")
    comments = CommentSerializer(many=True, source="question_comments")

    class Meta:
        model = QuestionModel
        fields = [
            "question_type",
            "question_text",
            "is_active",
            "created_on",
            "edited_on",
            "answers",
            "comments"
        ]

    def update(self, instance, validated_data):
        answers_data = validated_data.pop('question_choices', [])
        answers = instance.question_choices.all()
        instance.save()
        for answer_data in answers_data:
            answer_id = answer_data.get('pk', None)
            try:
                answer = answers.get(id=answer_id, question=instance)
                answer.choice_text = answer_data.get('choice_text', answer.choice_text)
                answer.votes = answer_data.get('votes', answer.votes)
                answer.save()
            except ObjectDoesNotExist:
                try:
                    ChoiceModel.objects.create(question=instance, **answer_data)
                except IntegrityError:
                    raise ApplicationError("Answer with this Primary key already exists. "
                                           "No pk should be provided when creating new answer.")
        return instance


class ProductListSerializer(serializers.ModelSerializer):
    product_questions = QuestionSerializer(many=True, source="questions")

    class Meta:
        model = ProductModel
        fields = [
            "name",
            "product_questions",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = [
            "name",
        ]


class QuestionCreateSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, source="question_choices")

    class Meta:
        model = QuestionModel
        fields = [
            "question_type",
            "question_text",
            "is_active",
            "created_on",
            "edited_on",
            "answers",
        ]

    def create(self, validated_data):
        user = self.context.get("request").user
        product_id = self.context.get("request").parser_context.get("kwargs").get("pk")
        product = ProductModel.objects.get(pk=product_id)
        validated_data["owner"] = user
        validated_data["product"] = product

        answers_data = validated_data.pop("question_choices")

        question = QuestionModel.objects.create(**validated_data)

        answers = [ChoiceModel(question=question, **answer_data) for answer_data in answers_data]

        ChoiceModel.objects.bulk_create(answers)

        return question


# class QuestionRUDSerializer(serializers.ModelSerializer):
#     answers = AnswerSerializer(many=True, source="question_choices")
#     comments = CommentSerializer(many=True, source="")
#     class Meta:
#         model = QuestionModel
#         fields = [
#             "question_type",
#             "question_text",
#             "is_active",
#             "answers",
#             "comments",
#         ]
