from django.urls import reverse
from django.core.mail import send_mail, EmailMessage
from django.template.loader import get_template

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


def make_verify_abslurl(user, request):
    from django.contrib.sites.shortcuts import get_current_site

    current_site = get_current_site(request).domain
    relative_link = reverse("verify_email_api_view")

    token = RefreshToken.for_user(user).access_token

    abls_url = f"http://{current_site}{relative_link}?token={token}"

    return abls_url
