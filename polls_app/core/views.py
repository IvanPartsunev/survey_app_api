from django.db import IntegrityError
from rest_framework import status
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from polls_app.core.mixins import AnswerCommentsCreateMixin
from polls_app.core.permissions import IsOwner
from polls_app.core.selectors import ProductsSelector, QuestionSelector, AnswerSelector, CommentSelector
from polls_app.core.serializers import QuestionListSerializer, ProductListSerializer, ProductReadDeleteSerializer, \
    QuestionReadDeleteSerializer, QuestionCreateUpdateSerializer, ProductCreateUpdateSerializer, \
    AnswerReadDeleteSerializer, AnswerCreateUpdateSerializer, CommentCreateUpdateSerializer, CommentReadDeleteSerializer


class ProductsListApiView(views.GenericAPIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        """
        GET request returns list of all products for the user.
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE a product for the user.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        selector = ProductsSelector(self.request.user)
        queryset = selector.get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() in ["get", "delete"]:
            return ProductListSerializer
        elif self.request.method.lower() == "post":
            return ProductCreateUpdateSerializer


class ProductsApiView(views.GenericAPIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        """
        GET request retrieve product with given id and questions related to this product.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """
        PUT request edit product with the given id.
        """

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        """
        DELETE request product with the given id.
        """

        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        selector = ProductsSelector(self.request.user)
        queryset = selector.get_queryset().select_related("owner").prefetch_related("questions")
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() in ["get", "delete"]:
            return ProductReadDeleteSerializer
        elif self.request.method.lower() == "put":
            return ProductCreateUpdateSerializer


class QuestionsListApiView(views.GenericAPIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        """
        GET request returns list of all questions for the product.
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE a question for the product.\
        ***Allowed types: "Single choice", "Multiple choices".
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user, product_id=self.kwargs.get("product_pk"))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        selector = QuestionSelector(self.request.user, self.kwargs.get("product_pk"))
        queryset = selector.get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() in ["get", "delete"]:
            return QuestionListSerializer
        elif self.request.method.lower() == "post":
            return QuestionCreateUpdateSerializer


class QuestionsApiView(views.GenericAPIView):
    lookup_fields = ["product_pk", "question_pk"]
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        """
        GET request retrieve question with the given id.
        """

        question = self.get_object()
        if question:
            serializer = self.get_serializer(question)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Didn't found question with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, *args, **kwargs):
        """
        PUT request edit question with the given id.
        """
        try:

            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(serializer.data, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(
                {"error": "Didn't found question with the given id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete question with the given id.
        """

        question = self.get_object()
        if question:
            question.delete()
            return Response(
                {"message": "Successfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"error": "Didn't found question with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_object(self):
        queryset = self.get_queryset()
        question_id = self.kwargs.get("question_pk")
        question = queryset.filter(id=question_id).first()

        return question

    def get_queryset(self):
        selector = QuestionSelector(self.request.user, self.kwargs.get("product_pk"))

        if self.request.method.lower() == "get":
            queryset = (selector.get_queryset()
                        .select_related("owner")
                        .prefetch_related("question_answers")
                        .prefetch_related("question_comments"))
            return queryset

        else:
            queryset = selector.get_queryset()
            return queryset

    def get_serializer_class(self):
        if self.request.method.lower() in ["get", "delete"]:
            return QuestionReadDeleteSerializer
        elif self.request.method.lower() == "put":
            return QuestionCreateUpdateSerializer


class AnswersApiView(views.GenericAPIView):
    lookup_fields = ["question_pk", "answer_pk"]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        queryset = self.get_queryset()
        answer_id = self.kwargs.get("answer_pk")
        answer = queryset.filter(id=answer_id).first()
        return answer

    def get_queryset(self):
        selector = AnswerSelector(self.kwargs.get("question_pk"))
        queryset = selector.get_queryset()
        return queryset


class AnswersCreateApiView(AnswersApiView, AnswerCommentsCreateMixin):
    serializer_class = AnswerCreateUpdateSerializer

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE an answer for the question.
        """
        return super().post(request, *args, **kwargs)


class AnswersReadUpdateDeleteApiView(AnswersApiView):
    def get(self, request, *args, **kwargs):
        """
        GET request retrieve an answer with the given id.
        """

        answer = self.get_object()
        if answer:
            serializer = self.get_serializer(answer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Didn't found answer with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, *args, **kwargs):
        """
        PUT request edit an answer with the given id.
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(
                {"error": "Didn't found answer with the given id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete an answer with the given id.
        """

        question = self.get_object()
        if question:
            question.delete()
            return Response(
                {"message": "Successfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"error": "Didn't found answer with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_serializer_class(self):
        if self.request.method.lower() in ["get", "delete"]:
            return AnswerReadDeleteSerializer
        elif self.request.method.lower() == "put":
            return AnswerCreateUpdateSerializer


class CommentsApiView(views.GenericAPIView):
    lookup_fields = ["product_pk", "question_pk", "comment_pk"]
    permission_classes = [IsAuthenticated, IsOwner]

    def get_object(self):
        queryset = self.get_queryset()
        comment_id = self.kwargs.get("comment_pk")
        comment = queryset.filter(id=comment_id).first()
        return comment

    def get_queryset(self):
        selector = CommentSelector(self.kwargs.get("question_pk"))
        queryset = selector.get_queryset()
        return queryset


class CommentsCreateApiView(CommentsApiView, AnswerCommentsCreateMixin):
    serializer_class = CommentCreateUpdateSerializer

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE a comment for the question.
        """
        return super().post(request, *args, **kwargs)


class CommentsReadUpdateDeleteApiView(CommentsApiView):
    def get(self, request, *args, **kwargs):
        """
        GET request retrieve an answer with the given id.
        """

        comment = self.get_object()
        if comment:
            serializer = self.get_serializer(comment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(
            {"error": "Didn't found comment with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def put(self, request, *args, **kwargs):
        """
        PUT request edit an answer with the given id.
        """

        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(
                {"error": "Didn't found comment with the given id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete an answer with the given id.
        """

        comment = self.get_object()
        if comment:
            comment.delete()
            return Response(
                {"message": "Successfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"error": "Didn't found comment with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_serializer_class(self):
        if self.request.method.lower() in ["get", "delete"]:
            return CommentReadDeleteSerializer
        elif self.request.method.lower() == "put":
            return CommentCreateUpdateSerializer
