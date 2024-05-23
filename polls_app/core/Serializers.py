from rest_framework import serializers

from polls_app.core.models import QuestionModel, ChoiceModel, CommentModel, ProductModel


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChoiceModel
        fields = [
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


class ProductQuestionSerializer(serializers.ModelSerializer):
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
