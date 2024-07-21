from django.contrib.auth import get_user_model
from django.db import models, IntegrityError

from rest_framework import status
from rest_framework.response import Response


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
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(question_id=self.kwargs.get("question_pk"))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response(
                {"error": "Didn't found question with the given id"},
                status=status.HTTP_400_BAD_REQUEST,
            )


