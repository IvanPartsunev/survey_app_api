from rest_framework import serializers

from polls_app.core.models import QuestionModel, AnswerModel, CommentModel, ProductModel


class AnswerCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            "answer_text",
        ]


class AnswerReadDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            "pk",
            "answer_text",
            "votes",
            "created_on",
            "edited_on",
        ]


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = [
            "comment_text",
        ]


class CommentReadDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = [
            "pk",
            "comment_text",
            "created_on",
            "edited_on",
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionModel
        fields = [
            "pk",
            "question_type",
            "question_text",
            "is_active",
            "created_on",
            "edited_on",
        ]


class QuestionReadDeleteSerializer(serializers.ModelSerializer):
    answers = AnswerReadDeleteSerializer(many=True, source="question_answers")
    comments = CommentReadDeleteSerializer(many=True, source="question_comments", required=False)

    class Meta:
        model = QuestionModel
        fields = [
            "pk",
            "question_type",
            "question_text",
            "is_active",
            "answers",
            "comments",
        ]


class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionModel
        fields = [
            "question_type",
            "question_text",
        ]


class ProductReadDeleteSerializer(serializers.ModelSerializer):
    product_questions = QuestionListSerializer(many=True, source="questions")

    class Meta:
        model = ProductModel
        fields = [
            "pk",
            "name",
            "created_on",
            "edited_on",
            "product_questions",
        ]


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductModel
        fields = [
            "name",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    product_questions = QuestionReadDeleteSerializer(many=True, source="questions")

    class Meta:
        model = ProductModel
        fields = [
            "pk",
            "name",
            "created_on",
            "edited_on",
            "product_questions",
        ]
