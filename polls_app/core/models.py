from django.db import models
from django.utils.translation import gettext_lazy as _

from polls_app.core.mixins import CreateUpdateMixin

class QuestionModel(CreateUpdateMixin):
    class QuestionType(models.TextChoices):
        ONE_CHOICE = "ONE", _("Single choice")
        MULTIPLE_CHOICES = "MLT", _("Multiple choices")
        TEXT = "TXT", _("Custom choice")
    
    question_type = models.CharField(choices=QuestionType)

    question_text = models.CharField(
        max_length=255,
        null=False,
        blank=False,
    )


class ChoiceModel(CreateUpdateMixin):
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    queestion = models.ForeignKey(
        "QuestionModel", 
        on_delete=models.CASCADE, 
        related_name="question"
        )

class CommentModel(CreateUpdateMixin):
    comment = models.TextField(max_length=100) 