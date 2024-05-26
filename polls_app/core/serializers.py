from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.response import Response

from polls_app.core.models import QuestionModel, AnswerModel, CommentModel, ProductModel
from polls_app.custom_exeption import ApplicationError


class AnswerSerializer(serializers.ModelSerializer):
    """
    If no pk is provided, a new answer will be created.
    """
    pk = serializers.IntegerField(required=False)

    class Meta:
        model = AnswerModel
        fields = [
            "pk",
            "answer_text",
            "votes",
            "created_on",
            "edited_on",
        ]


class AnswerDeleteSerializer(serializers.ModelSerializer):

    question_pk = serializers.IntegerField(
        required=True,
        help_text="ID of the question to which the answer belongs"
    )

    class Meta:
        model = AnswerModel
        fields = [
            "question_pk"
        ]


class CommentSerializer(serializers.ModelSerializer):

    question_pk = serializers.IntegerField(
        required=True,
        help_text="ID of the question to which the comment belongs"
    )

    class Meta:
        model = CommentModel
        fields = [
            "pk",
            "comment",
            "created_on",
            "edited_on",
            "question_pk"
        ]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, source="question_choices")
    comments = CommentSerializer(many=True, source="question_comments", required=False)

    class Meta:
        model = QuestionModel
        fields = [
            "pk",
            "question_type",
            "question_text",
            "is_active",
            "created_on",
            "edited_on",
            "answers",
            "comments"
        ]

    def update(self, instance, validated_data):
        validated_data.pop("question_comments", [])
        answers_data = validated_data.pop('question_choices', [])
        answers = instance.question_choices.all()

        for answer_data in answers_data:
            answer_id = answer_data.get('pk', None)
            try:
                answer = answers.get(id=answer_id, question=instance)
                answer.answer_text = answer_data.get('answer_text', answer.answer_text)
                answer.votes = answer_data.get('votes', answer.votes)
                answer.save()
            except ObjectDoesNotExist:
                try:
                    AnswerModel.objects.create(question=instance, **answer_data)
                except IntegrityError:
                    raise ApplicationError("Answer with this Primary key already exists for another user. "
                                           "No pk should be provided when creating new answer.")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance


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

        answers = [AnswerModel(question=question, **answer_data) for answer_data in answers_data]

        AnswerModel.objects.bulk_create(answers)

        return question


class ProductListSerializer(serializers.ModelSerializer):
    product_questions = QuestionSerializer(many=True, source="questions")

    class Meta:
        model = ProductModel
        fields = [
            "pk",
            "name",
            "product_questions",
        ]


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = [
            "name",
        ]

