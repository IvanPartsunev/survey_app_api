from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework import generics as views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from polls_app.custom_exeption import ApplicationError


class CreateUpdateMixin(models.Model):
    created_on = models.DateField(auto_now_add=True)
    edited_on = models.DateField(auto_now=True)

    class Meta:
        abstract = True


class AnswerAndCommentDeleteMixin(views.DestroyAPIView):

    model = None
    serializer_class = None
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        question_pk = self.request.data.get("context", {}).get("question_pk")
        queryset = self.model.objects.filter(question_id=question_pk)
        return queryset

    def get_object(self):
        try:
            return super().get_object()
        except ObjectDoesNotExist:
            raise ApplicationError("No question matches given pk")

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {"message": "Successfully deleted"},
            status=status.HTTP_200_OK
        )
