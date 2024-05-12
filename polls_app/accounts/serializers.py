from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


UserModel = get_user_model()


class AccountCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        error_messages={"blank": "This field is requied."}
    )

    class Meta:
        model = UserModel
        fields = (
            "pk",
            "email",
            "password",
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)

    def to_representation(self, *args, **kwargs):
        representation = super().to_representation(*args, **kwargs)
        representation.pop("password", None)
        return representation


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        return data
