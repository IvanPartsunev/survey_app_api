from django.contrib.auth import get_user_model
from django.db import models, IntegrityError

from rest_framework import status
from rest_framework.response import Response

from polls_app.core.models import QuestionModel
from polls_app.core.permissions import IsOwner

UserModel = get_user_model()


class CreateUpdateOwnerMixin(models.Model):
    created_on = models.DateField(auto_now_add=True)
    edited_on = models.DateField(auto_now=True)
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class AnswerCommentsCreateMixin:
    serializer_class = None

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = QuestionModel.objects.filter(id=self.kwargs.get("question_pk"))

        IsOwner.question_permission_check(question, request.user)

        serializer.save(question=question)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



