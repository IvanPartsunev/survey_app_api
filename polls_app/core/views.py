from django.shortcuts import get_object_or_404
from rest_framework import views as api_views, status
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import views as api_views

from polls_app.core.mixins import AnswerAndCommentDeleteMixin
from polls_app.core.permissions import IsOwner
from polls_app.core.selectors import ProductsSelector, QuestionSelector
from polls_app.core.serializers import (QuestionListSerializer, ProductListSerializer, ProductSerializer,
                                        AnswerDeleteSerializer, CommentSerializer, CommentDeleteSerializer,
                                        QuestionCreateSerializer)
from polls_app.core.models import QuestionModel, ProductModel, AnswerModel, CommentModel
from polls_app.custom_exeption import ApplicationError


class ProductsApiView(views.GenericAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        selector = ProductsSelector(self.request.user)
        queryset = selector.get_queryset().prefetch_related("questions").prefetch_related("answers")
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return ProductListSerializer
        elif self.request.method.lower() == "post":
            return ProductSerializer


class ProductApiView(views.GenericAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        selector = ProductsSelector(self.request.user)
        queryset = selector.get_queryset().select_related("owner").prefetch_related("questions")
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return ProductListSerializer
        elif self.request.method.lower() in ["put", "patch"]:
            return ProductSerializer
        elif self.request.method.lower() == "delete":
            return ProductListSerializer


class QuestionsApiView(views.GenericAPIView):
    serializer_class = ProductListSerializer
    lookup_field = "product_pk"
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=self.request.user, product_id=self.kwargs.get("product_pk"))
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        selector = QuestionSelector(self.request.user, self.kwargs.get("product_pk"))
        queryset = (selector.get_queryset()
                    .select_related("owner")
                    .prefetch_related("question_choices")
                    .prefetch_related("question_comments"))
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return QuestionListSerializer
        elif self.request.method.lower() == "post":
            return QuestionCreateSerializer


# class ProductsCreateApiView(views.CreateAPIView):
#     """
#     Create only the product.
#     """
#     serializer_class = ProductCreateSerializer
#     permission_classes = [IsAuthenticated]
#
#     def perform_create(self, serializer):
#         serializer.validated_data["owner"] = self.request.user
#         serializer.save()
#
#
# class ProductsListApiView(views.ListAPIView):
#     """
#     Display all products for the user with related questions, answers and comments.
#     """
#     serializer_class = ProductListSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = (ProductModel.objects
#                     .prefetch_related("questions")
#                     .filter(owner=self.request.user))
#         return queryset
#
#
# class QuestionCreateApiView(views.CreateAPIView):
#     """
#     Create question for product and answers.
#     """
#
#     serializer_class = QuestionCreateSerializer
#     permission_classes = [IsAuthenticated]
#
#
# class QuestionsListApiView(views.ListAPIView):
#     """
#     Display all questions for the User with answers and comments.
#     """
#     serializer_class = QuestionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_queryset(self):
#         queryset = (QuestionModel.objects
#                     .prefetch_related("question_choices", "question_comments")
#                     .filter(owner=self.request.user))
#         return queryset
#
#
# class QuestionRUDApiView(views.RetrieveUpdateDestroyAPIView):
#     """
#     - Handle Create, update and delete questions.
#     - Handles answers creation and update.
#     - Answer can be created or updated only in this view.
#     - Unlike the update, when new answer is created, no pk should be provided in data for the new answer.
#     - Answer creation and update are handled in PUT request.
#
#     """
#
#     serializer_class = QuestionSerializer
#     permission_classes = [IsAuthenticated, IsOwner]
#
#     def get_queryset(self):
#         queryset = (QuestionModel.objects
#                     .prefetch_related("question_choices", "question_comments")
#                     .filter(owner=self.request.user))
#         return queryset
#
#     def get_object(self):
#         queryset = self.get_queryset()
#         question = get_object_or_404(queryset, id=self.kwargs["pk"])
#         self.check_object_permissions(self.request, question)
#
#         return question
#
#     def put(self, request, *args, **kwargs):
#         try:
#             return super().put(request, *args, **kwargs)
#         except ApplicationError as error:
#             error_message = str(error)
#             return Response(
#                 {"error": error_message},
#                 status=status.HTTP_409_CONFLICT,
#             )
#
#     def patch(self, request, *args, **kwargs):
#         question = self.get_object()
#         question.is_active = not question.is_active
#         question.save()
#
#         serializer = self.get_serializer(question)
#         question_data = serializer.data
#
#         return Response(question_data)
#
#
# class AnswerDeleteApiView(AnswerAndCommentDeleteMixin):
#     """
#     Handle answer deletion.
#     Related question pk as context should be provided. {"context": "question_pk": 0}
#
#     """
#     model = AnswerModel
#     serializer_class = AnswerDeleteSerializer
#     permission_classes = [IsAuthenticated]
#
#
# class CommentListCreateApiView(views.ListCreateAPIView):
#     """
#     Create comment and listing comments for question.
#     No authentication is needed.
#     """
#     serializer_class = CommentSerializer
#     permission_classes = [AllowAny]
#
#
# class CommentApiView(AnswerAndCommentDeleteMixin, views.UpdateAPIView):
#     """
#     Handle Comment update and delete.
#     Related question pk as context should be provided. {"context": "question_pk": 0}
#     Permission classes are set to AllowAny.
#     """
#     model = CommentModel
#     permission_classes = [AllowAny]
#
#     def get_serializer_class(self):
#         if self.request.method == "DELETE":
#             return CommentDeleteSerializer
#         return CommentSerializer

