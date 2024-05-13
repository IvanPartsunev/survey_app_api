from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.http import urlsafe_base64_encode

from rest_framework_simplejwt.tokens import RefreshToken


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


def make_verification_url(user, request):
    from django.contrib.sites.shortcuts import get_current_site

    current_site = get_current_site(request).domain
    relative_link = reverse("verify_email_api_view")

    token = RefreshToken.for_user(user).access_token

    abls_url = f"http://{current_site}{relative_link}?token={token}"

    return abls_url


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


def make_password_reset_url(user, request):
    from django.contrib.sites.shortcuts import get_current_site

    current_site = get_current_site(request).domain
    relative_link = reverse("reset_password_api_view")

    encoded_pk = urlsafe_base64_encode(str(user.pk).encode())
    token = PasswordResetTokenGenerator().make_token(user)

    abls_url = f"http://{current_site}{relative_link}{encoded_pk}/{token}/"

    return abls_url