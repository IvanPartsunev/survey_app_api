from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from yaml import serialize

from polls_app.core.permissions import is_owner
from polls_app.core.services import get_object_and_check_permission_service
from polls_app.core.views_mixins import AnswerCommentsCreateMixin, AnswersApiMixin, CommentsApiMixin
from polls_app.core.models import ProductModel, QuestionModel
from polls_app.core.selectors import ProductsSelector, QuestionSelector, AnswerSelector, CommentSelector
from polls_app.core.serializers import QuestionListSerializer, ProductListDisplaySerializer, \
    QuestionRetrieveSerializer, QuestionCreateSerializer, ProductCreateUpdateDeleteSerializer, \
    AnswerReadDeleteSerializer, AnswerCreateSerializer, CommentCreateUpdateSerializer, \
    CommentReadDeleteSerializer, QuestionUpdateDeleteSerializer


class ProductsListCreateApiView(views.GenericAPIView):
    permission_classes = [IsAuthenticated]

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
        if self.request.method.lower() == "get":
            return ProductListDisplaySerializer
        return ProductCreateUpdateDeleteSerializer


class ProductRetrieveUpdateDeleteApiView(views.GenericAPIView):
    permission_classes = [IsAuthenticated]

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
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if getattr(instance, '_prefetched_objects_cache', None):
                # If 'prefetch_related' has been applied to a queryset, we need to
                # forcibly invalidate the prefetch cache on the instance.
                instance._prefetched_objects_cache = {}

            return Response(
                {"message": "Product successfully updated", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        except IntegrityError:
            return Response(
                {"error": "Product with the given ID does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        """
        DELETE product with the given id.
        """

        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Successfully deleted"},
            status=status.HTTP_200_OK,
        )

    def get_queryset(self):
        selector = ProductsSelector(self.request.user)
        queryset = selector.get_queryset().select_related("owner").prefetch_related("questions")
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() in "get":
            return ProductListDisplaySerializer
        return ProductCreateUpdateDeleteSerializer


class QuestionCreateApiView(views.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionCreateSerializer

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE a question for the product.\
        ***Allowed types: "Single choice", "Multiple choices".
        """

        user = self.request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product_pk = serializer.initial_data.get("product_id")

        product = get_object_and_check_permission_service("core", "productmodel", product_pk, user)

        serializer.save(owner=user, product=product)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class QuestionRetrieveUpdateDeleteApiView(views.GenericAPIView):
    permission_classes = [IsAuthenticated]

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

            return Response(
                {"message": "Question successfully updated.", "data": serializer.data},
                status = status.HTTP_200_OK,
            )

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
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Didn't found question with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_object(self):
        queryset = self.get_queryset()
        question_id = self.kwargs.get("pk")
        question = queryset.filter(id=question_id).first()

        return question

    def get_queryset(self):
        selector = QuestionSelector(self.request.user, self.kwargs.get("pk"), self.request.method)
        queryset = selector.get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return QuestionRetrieveSerializer
        return QuestionUpdateDeleteSerializer


class AnswersCreateApiView(views.GenericAPIView, AnswersApiMixin, AnswerCommentsCreateMixin):
    permission_classes = [IsAuthenticated]
    serializer_class = AnswerCreateSerializer

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE an answer for the question.
        """
        serializer = self.get_serializer()
        serializer.is_valid(raise_exception=True)
        question_id = serializer.initial_data.get("question_id")

        question = get_object_and_check_permission_service("core", "questionmodel", question_id, None)

        serializer.save(question=question)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnswersReadUpdateDeleteApiView(AnswersApiMixin, views.GenericAPIView):
    lookup_fields = ["question_pk", "answer_pk"]
    permission_classes = [IsAuthenticated]

    # def get(self, request, *args, **kwargs):
    #     """
    #     GET request retrieve an answer with the given id.
    #     """
    #     question = self.get_question(self.kwargs)
    #     IsOwner.question_permission_check(question, request.user)
    #
    #     answer = self.get_object()
    #     if answer:
    #         serializer = self.get_serializer(answer)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(
    #         {"error": "Didn't found answer with the given id"},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    def put(self, request, *args, **kwargs):
        """
        PUT request edit an answer with the given id.
        """
        try:

            question = self.get_question(self.kwargs)
            IsOwner.question_permission_check(question, request.user)

            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"message": "Answer successfully updated.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        except IntegrityError:
            return Response(
                {"error": "Didn't found answer with the given id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete an answer with the given id.
        """

        question = self.get_question(self.kwargs)
        IsOwner.question_permission_check(question, request.user)

        question = self.get_object()
        if question:
            question.delete()
            return Response(
                {"message": "Successfully deleted"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"error": "Didn't found answer with the given id"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get_serializer_class(self):
        if self.request.method.lower() in ["get", "delete"]:
            return AnswerReadDeleteSerializer
        elif self.request.method.lower() == "put":
            return AnswerCreateSerializer


class CommentsCreateApiView(views.GenericAPIView, AnswerCommentsCreateMixin):
    lookup_fields = ["question_pk", "comment_pk"]
    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateUpdateSerializer

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE a comment for the question.
        """
        return super().post(request, *args, **kwargs)


class CommentsReadUpdateDeleteApiView(CommentsApiMixin, views.GenericAPIView):
    lookup_fields = ["question_pk", "comment_pk"]
    permission_classes = [IsAuthenticated]

    # def get(self, request, *args, **kwargs):
    #     """
    #     GET request retrieve an answer with the given id.
    #     """
    #
    #     question = self.get_question(self.kwargs)
    #     IsOwner.question_permission_check(question, request.user)
    #
    #     comment = self.get_object()
    #     if comment:
    #         serializer = self.get_serializer(comment)
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(
    #         {"error": "Didn't found comment with the given id"},
    #         status=status.HTTP_400_BAD_REQUEST,
    #     )

    def put(self, request, *args, **kwargs):
        """
        PUT request edit an answer with the given id.
        """

        try:

            question = self.get_question(self.kwargs)
            IsOwner.question_permission_check(question, request.user)

            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                {"message": "Comment successfully updated.", "data": serializer.data},
                status=status.HTTP_200_OK,
            )

        except IntegrityError:
            return Response(
                {"error": "Didn't found comment with the given id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete an answer with the given id.
        """

        question = self.get_question(self.kwargs)
        IsOwner.question_permission_check(question, request.user)

        comment = self.get_object()
        if comment:
            comment.delete()
            return Response(
                {"message": "Successfully deleted"},
                status=status.HTTP_200_OK,
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
