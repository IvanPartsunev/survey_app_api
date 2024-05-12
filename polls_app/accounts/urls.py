from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from polls_app.accounts.views import CreateAccountApiView, LoginAccountApiView


urlpatterns = (
    path("register/", CreateAccountApiView.as_view(), name="register_api_view"),
    path("login/", LoginAccountApiView.as_view(), name="login_api_view"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
)
