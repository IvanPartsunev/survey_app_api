from django.shortcuts import get_object_or_404
from rest_framework import views as api_views, status
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from polls_app.core.permissions import IsOwner
from polls_app.core.serializers import QuestionSerializer, ProductListSerializer, ProductCreateSerializer, \
    QuestionCreateSerializer
from polls_app.core.models import QuestionModel, ProductModel
from polls_app.custom_exeption import ApplicationError


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


class QuestionCreateApiView(views.CreateAPIView):
    """
    Create question for product and answers.
    """

    serializer_class = QuestionCreateSerializer
    permission_classes = [IsAuthenticated]


class QuestionRUDApiView(views.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        queryset = (QuestionModel.objects
                    .prefetch_related("question_choices", "question_comments")
                    .filter(owner=self.request.user))
        return queryset

    def get_object(self):
        queryset = self.get_queryset()
        question = get_object_or_404(queryset, id=self.kwargs["pk"])
        self.check_object_permissions(self.request, question)

        return question

    def put(self, request, *args, **kwargs):
        try:
            return super().put(request, *args, **kwargs)
        except ApplicationError as error:
            error_message = str(error)
            return Response(
                {"error": error_message},
                status=status.HTTP_409_CONFLICT,
            )

    def patch(self, request, *args, **kwargs):
        question = self.get_object()
        question.is_active = not question.is_active
        question.save()

        serializer = self.get_serializer(question)
        question_data = serializer.data

        return Response(question_data)



