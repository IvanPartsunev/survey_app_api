from rest_framework import generics as api_views, permissions
from django.contrib.auth import get_user_model
from polls_app.accounts.serializers import AccountCreateSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


UserModel = get_user_model()

class CreateAccountApiView(api_views.CreateAPIView):
    serializer_class = AccountCreateSerializer
    queryset = UserModel.objects.all()
    permission_classes = [permissions.AllowAny]
