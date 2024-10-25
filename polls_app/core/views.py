import uuid

from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from rest_framework import status
from rest_framework import generics as views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from polls_app.core.models import AnswerModel, CommentModel
from polls_app.core.permissions import IsAuthenticatedOrJWTGuest
from polls_app.core.services import get_object_and_check_permission_service, generate_comment_jwt_token_service, \
    validate_comment_uniqueness_service
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

        user = self.request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=user)
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

    def get_queryset(self):
        selector = QuestionSelector(self.request.user, self.kwargs.get("pk"), self.request.method)
        queryset = selector.get_queryset()
        return queryset

    def get_serializer_class(self):
        if self.request.method.lower() == "get":
            return QuestionRetrieveSerializer
        return QuestionUpdateDeleteSerializer


class AnswersCreateApiView(views.GenericAPIView):
    """
    This view creates answer for question. Question id should be provided as data in request.
    """
    queryset = AnswerModel.objects.all()
    serializer_class = AnswerCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE an answer for the question.
        """

        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question_id = serializer.initial_data.get("question_id")

        question = get_object_and_check_permission_service("core", "questionmodel", question_id, None)

        serializer.save(question=question, owner=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class AnswersUpdateDeleteApiView(UpdateDeleteMixin, views.GenericAPIView):
    """
    Trough this view Answer objects can be updated or deleted.
    """
    queryset = AnswerModel.objects.all()
    serializer_class = AnswerUpdateDeleteSerializer
    permission_classes = [IsAuthenticated]


class CommentsCreateApiView(views.GenericAPIView):
    """
    This view creates comment for question. Question id should be provided as data in request.
    """
    queryset = CommentModel.objects.all()
    serializer_class = CommentCreateSerializer
    permission_classes = [AllowAny]

    @method_decorator(ratelimit(key="ip", rate="15/h", method="POST", block=True))
    def post(self, request, *args, **kwargs):

        user = request.user

        if user.is_authenticated:
            created_by = user.username
        else:
            created_by = request.data.get("created_by", "Unknown")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question_id = serializer.initial_data.get("question_id")

        question = get_object_and_check_permission_service("core", "questionmodel", question_id, None)

        # If user is anonymous, handle JWT for comment limitation
        if not user.is_authenticated:
            token = request.COOKIES.get("anonymous_user_token", None)
            try:
                # Validate if a comment already exists for this question in the JWT payload
                validate_comment_uniqueness_service(question_id, token)
            except ValueError as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )

        comment = serializer.save(question=question, created_by=created_by)
        response = Response(serializer.data, status=status.HTTP_201_CREATED)

        if not user.is_authenticated:
            token = request.COOKIES.get("anonymous_user_token", None)
            token = generate_comment_jwt_token_service(comment.id, question_id, token)
            response.set_cookie("anonymous_user_token", token, httponly=True, max_age=60 * 60 * 24)  # 1 day expiration

        return response


class CommentsUpdateDeleteApiView(UpdateDeleteMixin, views.GenericAPIView):
    """
    Trough this view Comment objects can be updated or deleted.
    """
    queryset = CommentModel.objects.all()
    serializer_class = CommentUpdateDeleteSerializer
    permission_classes = [IsAuthenticatedOrJWTGuest]
