from rest_framework import views as api_views, status
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from polls_app.core.Serializers import QuestionSerializer, ProductListSerializer, ProductCreateSerializer, \
    ProductQuestionSerializer
from polls_app.core.models import QuestionModel, ProductModel


class QuestionsListApiView(views.ListAPIView):
    """
    Display all questions for the User with answers and comments.
    """
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (QuestionModel.objects
                    .prefetch_related("question_choices", "question_comments")
                    .filter(owner=self.request.user))
        return queryset


class ProductsListApiView(views.ListAPIView):
    """
    Display all products for the user with related questions, answers and comments.
    """
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = (ProductModel.objects
                    .prefetch_related("questions")
                    .filter(owner=self.request.user))
        return queryset


class ProductsCreateApiView(views.CreateAPIView):
    """
    Create only the product.
    """
    serializer_class = ProductCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.validated_data["owner"] = self.request.user
        serializer.save()


class ProductQuestionApiView(views.CreateAPIView):
    """
    Create question for product and answers.
    """

    serializer_class = ProductQuestionSerializer
    permission_classes = [IsAuthenticated]





