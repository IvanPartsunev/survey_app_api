from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from polls_app.accounts.models import AccountModel
from polls_app.core.mixins import CreateUpdateMixin

UserModel = get_user_model()


class ProductModel(CreateUpdateMixin):
    name = models.CharField(
        max_length=150,
    )
    owner = models.ForeignKey(
        AccountModel,
        on_delete=models.CASCADE,
        related_name="product_owner",
    )


class QuestionModel(CreateUpdateMixin):
    class QuestionType(models.TextChoices):
        ONE_CHOICE = "Single choice", _("Single choice")
        MULTIPLE_CHOICES = "Multiple choices", _("Multiple choices")
        TEXT = "Text", _("Text")

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

    owner = models.ForeignKey(
        AccountModel,
        on_delete=models.CASCADE,
        related_name="question_owner",
    )

    product = models.ForeignKey(
        ProductModel,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    def __str__(self):
        return self.question_text


class AnswerModel(CreateUpdateMixin):
    answer_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_choices"
        )

    def __str__(self):
        return self.answer_text


class CommentModel(CreateUpdateMixin):
    comment_text = models.TextField(max_length=255)
    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_comments"
    )

    def __str__(self):
        return self.comment_text
