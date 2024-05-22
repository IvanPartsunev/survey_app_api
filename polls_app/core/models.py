from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from polls_app.accounts.models import AccountModel
from polls_app.core.mixins import CreateUpdateMixin

UserModel = get_user_model()


class QuestionModel(CreateUpdateMixin):
    class QuestionType(models.TextChoices):
        ONE_CHOICE = "ONE", _("Single choice")
        MULTIPLE_CHOICES = "MLT", _("Multiple choices")
        TEXT = "TXT", _("Open answer")

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
        related_name="owner",
    )


class ChoiceModel(CreateUpdateMixin):
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_choices"
        )


class CommentModel(CreateUpdateMixin):
    comment = models.TextField(max_length=255)
    question = models.ForeignKey(
        QuestionModel,
        on_delete=models.CASCADE,
        related_name="question_comments"
    )
