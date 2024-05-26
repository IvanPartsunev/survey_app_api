from django.db import models
from rest_framework import generics as views, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


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
        question_id = self.request.data.get("question_pk", None)
        queryset = self.model.objects.filter(question_id=question_id)
        return queryset

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {"message": "Successfully deleted"},
            status=status.HTTP_200_OK
        )
