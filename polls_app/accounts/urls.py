from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from polls_app.accounts.views import CreateAccountApiView, LoginAccountApiView, VerifyEmailApiView, \
    PasswordResetConfirmApiView, PasswordResetApiView, GoogleCallbackApi, GoogleLoginRedirectApi

urlpatterns = (
    path("register/", CreateAccountApiView.as_view(), name="register_api_view"),
    path("login/", LoginAccountApiView.as_view(), name="login_api_view"),
    path("verify-email/", VerifyEmailApiView.as_view(), name="verify_email_api_view"),
    path("reset-password/", PasswordResetApiView.as_view(), name="reset_password_api_view"),
    path("reset-password/<str:encoded_pk>/<str:token>/", PasswordResetConfirmApiView.as_view(),
         name="reset_password_confirm_api_view"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("google-login/", GoogleCallbackApi.as_view(), name="google-login"),
    path("google-redirect/", GoogleLoginRedirectApi.as_view(), name="google-redirect"),
)
