import jwt

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import IntegrityError

from rest_framework import generics as api_views, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from polls_app.accounts.serializers import AccountCreateSerializer
from polls_app.accounts.utils import send_confirmation_email, make_verify_abslurl

UserModel = get_user_model()


class CreateAccountApiView(api_views.CreateAPIView):
    serializer_class = AccountCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"error": "Account with this email already exists."},
                status=status.HTTP_409_CONFLICT,
            )

    def perform_create(self, serializer):

        serializer.save()
        user_data = serializer.data
        user_email = user_data["email"]

        user = UserModel.objects.get(email=user_email)

        confirmation_url = make_verify_abslurl(user, self.request)

        send_confirmation_email(user_email, confirmation_url)


class LoginAccountApiView(TokenObtainPairView):
    queryset = UserModel.objects.all()
    permission_classes = [permissions.AllowAny]


class VerifyEmail(api_views.GenericAPIView):
    queryset = None
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        token = request.GET.get("token")

        try:
            secret_key = settings.SECRET_KEY
            payload = jwt.decode(token, secret_key, algorithms="HS256")
            user = UserModel.objects.get(id=payload["user_id"])

            user.is_active = True
            user.save()

            return Response(
                {"email": "Successfully activate"},
                status=status.HTTP_200_OK,
            )

        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activation expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid token"},
                status=status.HTTP_400_BAD_REQUEST,
            )
