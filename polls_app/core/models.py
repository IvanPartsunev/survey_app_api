from django.db import models
from django.utils.translation import gettext_lazy as _

from polls_app.accounts.models import AccountModel
from polls_app.core.mixins import CreateUpdateOwnerMixin


class ProductModel(CreateUpdateOwnerMixin):
    name = models.CharField(
        max_length=150,
    )


class QuestionModel(CreateUpdateOwnerMixin):
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

    def __str__(self):
        return self.question_text


class AnswerModel(CreateUpdateOwnerMixin):
    answer_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_answers"
        )

    def __str__(self):
        return self.answer_text


class CommentModel(CreateUpdateOwnerMixin):
    comment_text = models.TextField(max_length=255)
    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_comments"
    )

    def __str__(self):
        return self.comment_text
