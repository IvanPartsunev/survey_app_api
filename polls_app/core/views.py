from django.db import IntegrityError
from rest_framework import status
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from polls_app.core.models import AnswerModel, CommentModel
from polls_app.core.services import get_object_and_check_permission_service
from polls_app.core.selectors import ProductsSelector, QuestionSelector
from polls_app.core.serializers import ProductListDisplaySerializer, QuestionRetrieveSerializer, \
    QuestionCreateSerializer, ProductCreateUpdateDeleteSerializer, AnswerCreateSerializer, CommentCreateSerializer, \
    QuestionUpdateDeleteSerializer, AnswerUpdateDeleteSerializer, CommentUpdateDeleteSerializer
from polls_app.core.views_mixins import UpdateDeleteMixin


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


class ProductRetrieveUpdateDeleteApiView(UpdateDeleteMixin, views.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        GET request retrieve product with given id and questions related to this product.
        """

        instance = self.get_object()
        serializer = self.get_serializer(instance)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Patch request edit product with the given id.
        """
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        DELETE product with the given id.
        """
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        selector = ProductsSelector(self.request.user)
        queryset = selector.get_queryset()
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


class QuestionRetrieveUpdateDeleteApiView(UpdateDeleteMixin, views.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        GET request retrieve question with the given id.
        """

        question = self.get_object()
        serializer = self.get_serializer(question)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        """
        Patch request edit question with the given id.
        """
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete question with the given id.
        """
        return super().delete(request, *args, **kwargs)

    def get_queryset(self):
        selector = QuestionSelector(self.request.user, self.kwargs.get("pk"), self.request.method)
        queryset = selector.get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return QuestionRetrieveSerializer
        return QuestionUpdateDeleteSerializer


class AnswersCreateApiView(views.GenericAPIView):
    queryset = AnswerModel.objects.all()
    serializer_class = AnswerCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE an answer for the question.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question_id = serializer.initial_data.get("question_id")

        question = get_object_and_check_permission_service("core", "questionmodel", question_id, request.user)

        serializer.save(question=question, owner=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnswersReadUpdateDeleteApiView(UpdateDeleteMixin, views.GenericAPIView):
    queryset = AnswerModel.objects.all()
    serializer_class = AnswerUpdateDeleteSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Patch request edit an answer with the given id.
        """
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete answer with the given id.
        """
        return super().delete(request, *args, **kwargs)


class CommentsCreateApiView(views.GenericAPIView):
    queryset = CommentModel.objects.all()
    permission_classes = [AllowAny]
    serializer_class = CommentCreateSerializer

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE a comment for the question.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question_id = serializer.initial_data.get("question_id")

        question = get_object_and_check_permission_service("core", "questionmodel", question_id, None)

        serializer.save(question=question)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentsUpdateDeleteApiView(UpdateDeleteMixin, views.GenericAPIView):
    queryset = CommentModel.objects.all()
    serializer_class = CommentUpdateDeleteSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        """
        Patch request edit a comment with the given id.
        """
        return super().patch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete answer with the given id.
        """
        return super().delete(request, *args, **kwargs)
