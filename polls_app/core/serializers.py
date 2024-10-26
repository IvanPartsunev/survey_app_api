from rest_framework import serializers

from polls_app.core.models import QuestionModel, AnswerModel, CommentModel, ProductModel


class CommentCreateSerializer(serializers.ModelSerializer):
    question_id = serializers.IntegerField(write_only=True)
    honeypot = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = CommentModel
        fields = [
            "id",
            "question_id",
            "created_by",
            "comment_text",
            "honeypot",
        ]

    def validate(self, data):
        if data.get("honeypot"):
            raise serializers.ValidationError("Spam detected.")

        return data

    def create(self, validated_data):
        # Remove the honeypot field before saving the object
        validated_data.pop('honeypot', None)

        return super().create(validated_data)

class CommentUpdateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommentModel
        fields = [
            "id",
            "comment_text",
        ]


class CommentRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentModel
        fields = [
            "id",
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
            "id",
            "question_id",
            "answer_text",
        ]


class AnswerUpdateDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = AnswerModel
        fields = [
            "id",
            "answer_text",
        ]


class AnswerRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnswerModel
        fields = [
            "id",
            "answer_text",
            "votes",
            "created_on",
            "edited_on",
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionModel
        fields = [
            "id",
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
            "id",
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
            "id",
            "name",
            "created_on",
            "edited_on",
            "product_questions",
        ]
