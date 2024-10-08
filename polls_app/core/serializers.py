from rest_framework import serializers

from polls_app.core.models import QuestionModel, AnswerModel, CommentModel, ProductModel


class CommentCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CommentModel
        fields = [
            "question_id",
            "created_by",
            "comment_text",
        ]


class CommentUpdateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentModel
        fields = [
            "comment_text",
        ]


class CommentRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = [
            "pk",
            "comment_text",
            "created_on",
            "edited_on",
            "created_by",
        ]


class AnswerCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = AnswerModel
        fields = [
            "question_id",
            "answer_text",
        ]


class AnswerUpdateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerModel
        fields = [
            "answer_text",
        ]

class AnswerRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            "pk",
            "answer_text",
            "votes",
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


class QuestionRetrieveSerializer(serializers.ModelSerializer):
    answers = AnswerRetrieveSerializer(many=True, source="question_answers")
    comments = CommentRetrieveSerializer(many=True, source="question_comments", required=False)

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


class QuestionCreateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = QuestionModel
        fields = [
            "id",
            "product_id",
            "question_type",
            "question_text",
        ]

class QuestionUpdateDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = QuestionModel
        fields = [
            "id",
            "question_type",
            "question_text",
        ]


class ProductCreateUpdateDeleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = ProductModel
        fields = [
            "id",
            "name",
        ]


class ProductListDisplaySerializer(serializers.ModelSerializer):
    product_questions = QuestionRetrieveSerializer(many=True, source="questions")

    class Meta:
        model = ProductModel
        fields = [
            "pk",
            "name",
            "created_on",
            "edited_on",
            "product_questions",
        ]
