from rest_framework import serializers
from django.contrib.auth import get_user_model

UserModel = get_user_model()
class AccountCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = (
            "pk",
            "email",
            "password",
        )

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)
    
    def to_representation(self, *args, **kwargs):
        representation = super().to_representation(*args, **kwargs)
        representation.pop('password', None)
        return representation
    

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)

        return data