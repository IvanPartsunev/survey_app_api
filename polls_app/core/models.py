from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from polls_app.accounts.models import AccountModel
from polls_app.core.models_mixins import CreateUpdateMixin

UserModel = get_user_model()

class ProductModel(CreateUpdateMixin):
    name = models.CharField(
        max_length=150,
    )

    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    @classmethod
    def class_name(cls):
        return "Product"


class QuestionModel(CreateUpdateMixin):
    class QuestionType(models.TextChoices):
        ONE_CHOICE = "Single choice", _("Single choice")
        MULTIPLE_CHOICES = "Multiple choices", _("Multiple choices")

    question_type = models.CharField(
        choices=QuestionType,
        max_length=max(len(choice) for choice, _ in QuestionType.choices),
    )

    question_text = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )

    is_active = models.BooleanField(
        default=False,
    )

    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    @classmethod
    def class_name(cls):
        return "Question"

    def __str__(self):
        return self.question_text


class AnswerModel(CreateUpdateMixin):
    answer_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_answers"
        )

    owner = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE
    )

    @classmethod
    def class_name(cls):
        return "Answer"

    def __str__(self):
        return self.answer_text


class CommentModel(CreateUpdateMixin):
    comment_text = models.TextField(max_length=255)
    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_comments"
    )

    owner = models.TextField(
        max_length=30,
        default="Unknown"
    )

    anonymous_user_id = models.CharField(
        default="Reg"   # Registered user
    )

    @classmethod
    def class_name(cls):
        return "Comment"

    def __str__(self):
        return self.comment_text
