from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from polls_app.core.models import QuestionModel
from polls_app.core.permissions import is_owner
from polls_app.core.selectors import AnswerSelector, CommentSelector


class QuestionGetMixin:

    @staticmethod
    def get_question(kwargs):
        question = get_object_or_404(QuestionModel, id=kwargs.get("question_pk"))
        return question


class AnswersApiMixin(QuestionGetMixin):

    def get_object(self):
        queryset = self.get_queryset()
        answer_id = self.kwargs.get("answer_pk")
        answer = queryset.filter(id=answer_id).first()
        return answer

    def get_queryset(self):
        selector = AnswerSelector(self.kwargs.get("question_pk"))
        queryset = selector.get_queryset()
        return queryset


class CommentsApiMixin(QuestionGetMixin):

    def get_object(self):
        queryset = self.get_queryset()
        comment_id = self.kwargs.get("comment_pk")
        answer = queryset.filter(id=comment_id).first()
        return answer

    def get_queryset(self):
        selector = CommentSelector(self.kwargs.get("question_pk"))
        queryset = selector.get_queryset()
        return queryset

class AnswerCommentsCreateMixin:
    serializer_class = None

    def post(self, request, *args, **kwargs):

        question = QuestionGetMixin.get_question(self.kwargs)
        is_owner(question, request.user)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(question=question, owner=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)