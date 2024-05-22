from rest_framework import serializers

from polls_app.core.models import QuestionModel, ChoiceModel, CommentModel


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceModel
        fields = [
            "choice_text",
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
    answers = AnswerSerializer(many=True)
    comments = CommentSerializer(many=True)

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
