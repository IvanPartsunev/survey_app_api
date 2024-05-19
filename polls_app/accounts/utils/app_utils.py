from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.http import urlsafe_base64_encode

from rest_framework_simplejwt.tokens import RefreshToken

from polls_app import settings


def send_confirmation_email(email, confirmation_url):
    data = {
        "url": confirmation_url
    }

    message = get_template("confirmation_email.txt").render(data)

    email = EmailMessage(
        subject="Please confirm your email.",
        body=message,
        to=[email],
    )

    email.send()


def make_verification_url(user):

    current_site = settings.BASE_BACKEND_URL
    relative_link = reverse("verify_email_api_view")

    token = RefreshToken.for_user(user).access_token

    url = f"{current_site}{relative_link}?token={token}"

    return url


def send_reset_password_email(email, confirmation_url):
    data = {
        "url": confirmation_url
    }

    message = get_template("reset_password_email.txt").render(data)

    email = EmailMessage(
        subject="Reset your password.",
        body=message,
        to=[email],
    )

    email.send()


def make_password_reset_url(user):

    current_site = settings.BASE_BACKEND_URL
    relative_link = reverse("reset_password_api_view")

    encoded_pk = urlsafe_base64_encode(str(user.pk).encode())
    token = PasswordResetTokenGenerator().make_token(user)

    url = f"{current_site}{relative_link}{encoded_pk}/{token}/"

    return url

