import jwt

from django.contrib.auth import get_user_model
from django.conf import settings
from django.db import IntegrityError
from django.shortcuts import redirect

from drf_spectacular.utils import extend_schema

from rest_framework import generics as api_views, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from polls_app.accounts.serializers import (AccountCreateSerializer, EmailSerializer, PasswordResetSerializer,
                                            VerifyEmailSerializer, InputSocialSerializer, RedirectSerializer)
from polls_app.accounts.utils.app_utils import (send_confirmation_email, make_verification_url,
                                                make_password_reset_url, send_reset_password_email)
from polls_app.accounts.utils.facebook_utils import FacebookSdkLoinServices
from polls_app.accounts.utils.google_utils import GoogleSdkLoginFlowService

UserModel = get_user_model()


class CreateAccountApiView(api_views.CreateAPIView):
    """
    Register a User in DB.
    This is the entry point to start 'app registration' flow.
    """

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
    """
    Activates the User account when a received link is used.
    """
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
    """
    Sends password reset email to the User's email if user exists.
    If a user doesn't exist, return an error.
    This is the entry point to start 'password reset' flow.
    """

    AUTH_PROVIDER = "App auth"

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

        if user.auth_provider != self.AUTH_PROVIDER:
            return Response(
                {"error": "Cannot change password for registration with social network!"},
                status=status.HTTP_403_FORBIDDEN,
            )

        confirmation_url = make_password_reset_url(user)

        send_reset_password_email(email, confirmation_url)

        return Response(
            {"message": "Password reset email sent"},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmApiView(api_views.GenericAPIView):
    """
    Update the User password when a received link is used.
    """

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


class GoogleLoginRedirectApiView(PublicApi):
    """
    Redirects user to 'Google' to obtain tokens.
    This is the entry point to start the 'Google login' flow.
    """

    serializer_class = RedirectSerializer

    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        google_login_flow = GoogleSdkLoginFlowService()

        authorization_url, state = google_login_flow.get_authorization_url()

        request.session["google_oauth2_state"] = state

        return redirect(authorization_url)


class GoogleLoginApiView(PublicApi):
    """
    Perform Google login using the LoginAccountApiView.
    If an account doesn't exist in DB, it is created with credentials from Google id_token;
    'name' is used as username;
    'sub' claim is used as account password.

    """
    AUTH_PROVIDER = "Google"

    serializer_class = InputSocialSerializer

    def get(self, request, *args, **kwargs):
        input_serializer = InputSocialSerializer(data=request.GET)
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
            auth_provider = self.AUTH_PROVIDER
            user = google_login_flow.create_google_user(
                user_email,
                user_name,
                auth_provider,
                user_sub,
                user_is_verified
            )

        if user.auth_provider != self.AUTH_PROVIDER:
            return Response(
                {"error": "User already registered with another method of registration."},
                status=status.HTTP_409_CONFLICT
            )

        login_token = google_login_flow.login_google_user(user, user_sub, user_is_verified)

        return Response(login_token)


class FacebookLoginApiView(PublicApi):
    """
    Redirects user to 'Facebook' to obtain tokens.
    This is the entry point to start the 'Facebook login' flow.
    """
    def get(self, request):
        facebook_login_flow = FacebookSdkLoinServices()

        fb_auth_url, state = facebook_login_flow.get_authorization_url()

        request.session['oauth_state'] = state

        return redirect(fb_auth_url)


class FacebookRedirectApiView(PublicApi):
    """
    Perform Facebook login using the LoginAccountApiView.
    If an account doesn't exist in DB, it is created with credentials from Facebook;
    'name' is used as username;
    'facebook_id' claim is used as account password.

    """
    AUTH_PROVIDER = "Facebook"

    serializer_class = InputSocialSerializer

    @extend_schema(exclude=True)
    def get(self, request):
        input_serializer = InputSocialSerializer(data=request.GET)
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

        session_state = request.session.get('oauth_state')

        if session_state is None:
            return Response(
                {"error": "CSRF check failed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        del request.session["oauth_state"]

        if state != session_state:
            return Response(
                {'error': 'Invalid state parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not code:
            return Response(
                {'error': 'No code provided'},
                status=status.HTTP_400_BAD_REQUEST
            )

        facebook_login_flow = FacebookSdkLoinServices()

        access_token = facebook_login_flow.get_token(code=code)

        user_info = facebook_login_flow.get_user_info(access_token=access_token)

        email = user_info.get('email')
        username = user_info.get('name')
        facebook_id = user_info.get('id')

        user = UserModel.objects.filter(email=email).first()

        if not user:
            auth_provider = self.AUTH_PROVIDER
            user = facebook_login_flow.create_facebook_user(email, username, auth_provider, facebook_id, True)

        if user.auth_provider != self.AUTH_PROVIDER:
            Response(
                {"error": "User already registered with another method of registration."},
                status=status.HTTP_409_CONFLICT
            )

        login_token = facebook_login_flow.login_facebook_user(user, facebook_id)

        return Response(login_token)
