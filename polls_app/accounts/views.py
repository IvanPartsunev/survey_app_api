import jwt

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import redirect

from rest_framework import generics as api_views, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from polls_app.accounts.serializers import AccountCreateSerializer, EmailSerializer, PasswordResetSerializer, \
    VerifyEmailSerializer, InputSerializer, RedirectSerializer
from polls_app.accounts.utils.app_utils import send_confirmation_email, make_verification_url, make_password_reset_url, \
    send_reset_password_email
from polls_app.accounts.utils.google_utils import GoogleSdkLoginFlowService

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

        confirmation_url = make_verification_url(user)

        send_confirmation_email(user_email, confirmation_url)


class VerifyEmailApiView(api_views.GenericAPIView):
    serializer_class = VerifyEmailSerializer
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


class PasswordResetApiView(api_views.GenericAPIView):
    queryset = None
    serializer_class = EmailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.data["email"]

        user = UserModel.objects.filter(email=email).first()

        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        confirmation_url = make_password_reset_url(user)

        send_reset_password_email(email, confirmation_url)

        return Response(
            {"message": "Password reset email sent"},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmApiView(api_views.GenericAPIView):
    serializer_class = PasswordResetSerializer
    permission_classes = [permissions.AllowAny]

    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data,
            context={"encoded_pk": kwargs["encoded_pk"], "token": kwargs["token"]}
        )

        serializer.is_valid(raise_exception=True)

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK,
        )


class LoginAccountApiView(TokenObtainPairView):
    queryset = UserModel.objects.all()
    permission_classes = [permissions.AllowAny]


class PublicApi(APIView):
    authentication_classes = ()
    permission_classes = ()


class GoogleLoginRedirectApi(PublicApi):
    serializer_class = RedirectSerializer

    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleSdkLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleCallbackApi(PublicApi):
    serializer_class = InputSerializer

    def get(self, request, *args, **kwargs):
        input_serializer = InputSerializer(data=request.GET)
        input_serializer.is_valid(raise_exception=True)

        validated_data = input_serializer.validated_data

        code = validated_data.get("code")
        error = validated_data.get("error")
        state = validated_data.get("state")

        if error is not None:
            return Response(
                {"error": error},
                status=status.HTTP_400_BAD_REQUEST
            )

        if code is None or state is None:
            return Response(
                {"error": "Code and state are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        session_state = request.session.get("google_oauth2_state")

        if session_state is None:
            return Response(
                {"error": "CSRF check failed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        del request.session["google_oauth2_state"]

        if state != session_state:
            return Response(
                {"error": "CSRF check failed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        google_login_flow = GoogleSdkLoginFlowService()

        google_tokens = google_login_flow.get_tokens(code=code, state=state)

        id_token_decoded = google_tokens.decode_id_token()

        user_email = id_token_decoded["email"]
        user_name = id_token_decoded["name"]
        user_sub = id_token_decoded["sub"]
        user_is_verified = id_token_decoded["email_verified"]

        user = UserModel.objects.filter(email=user_email).first()

        if not user:
            user = google_login_flow.create_google_user(user_email, user_name, user_sub, user_is_verified)

        login_token = google_login_flow.login_google_user(user, user_sub, user_is_verified)

        return Response(login_token)
