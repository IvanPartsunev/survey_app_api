from django.contrib.auth import get_user_model

from rest_framework import generics as api_views, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from polls_app.accounts.serializers import AccountCreateSerializer

UserModel = get_user_model()


class CreateAccountApiView(api_views.CreateAPIView):
    serializer_class = AccountCreateSerializer
    permission_classes = [permissions.AllowAny]


class LoginAccountApiView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]
