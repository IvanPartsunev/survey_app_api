from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

UserModel = get_user_model()


class AccountCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        error_messages={"blank": "This field is required."},
    )
    username = serializers.CharField(
        error_messages={"blank": "This field is required."},
    )
    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = UserModel
        fields = (
            "pk",
            "email",
            "username",
            "password",
        )

    def create(self, validated_data):
        return UserModel.objects.create_user(**validated_data)


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        fields = ("password",)

    def validate(self, data):
        password = data.get("password")
        token = self.context.get("token")
        encoded_pk = self.context.get("encoded_pk")

        if token is None or encoded_pk is None:
            raise serializers.ValidationError("Invalid token")

        pk = urlsafe_base64_decode(encoded_pk).decode()
        user = UserModel.objects.get(pk=pk)

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Invalid token")

        user.set_password(password)
        user.save()
        return data


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ("email",)


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        return data


class InputSerializer(serializers.Serializer):
    code = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    state = serializers.CharField(required=False)


class RedirectSerializer(serializers.Serializer):
    pass
