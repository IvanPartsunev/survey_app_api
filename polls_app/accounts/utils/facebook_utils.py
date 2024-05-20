import random
import string

import requests
from django.urls import reverse_lazy
from rest_framework.response import Response

from polls_app import settings
from polls_app.custom_exeption import ApplicationError

from django.contrib.auth import get_user_model

UserModel = get_user_model()


class FacebookSdkLoinServices:

    API_URI = reverse_lazy("facebook-redirect")
    APP_ID = settings.FACEBOOK_APP_ID

    def _get_redirect_uri(self):
        domain = settings.BASE_BACKEND_URL
        api_uri = self.API_URI
        redirect_uri = f"{domain}{api_uri}"
        return redirect_uri

    @staticmethod
    def _generate_state():
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def get_authorization_url(self):
        state = self._generate_state()
        redirect_uri = self._get_redirect_uri()

        authorization_url = (f"https://www.facebook.com/v10.0/dialog/oauth?"
                             f"client_id={self.APP_ID}"
                             f"&redirect_uri={redirect_uri}"
                             f"&state={state}"
                             f"&scope=email")

        return authorization_url, state

    def get_token(self, *, code):
        redirect_uri = self._get_redirect_uri()
        app_secret = settings.FACEBOOK_APP_SECRET
        token_url = (
            f"https://graph.facebook.com/v10.0/oauth/access_token?"
            f"client_id={self.APP_ID}"
            f"&redirect_uri={redirect_uri}"
            f"&client_secret={app_secret}"
            f"&code={code}"
        )

        token_response = requests.get(token_url)
        token_json = token_response.json()
        access_token = token_json.get('access_token')
        if not access_token:
            raise ApplicationError("Failed to obtain tokens from Facebook.")

        return access_token

    def get_user_info(self, *, access_token):
        user_info_url = (f"https://graph.facebook.com/me?"
                         f"access_token={access_token}"
                         f"&fields=id,name,email")

        user_info_response = requests.get(user_info_url)
        user_info = user_info_response.json()

        return user_info

    @staticmethod
    def create_facebook_user(email, user_name, auth_provider, facebook_id, is_active):
        user = UserModel.objects.create_user(
            email=email,
            username=user_name,
            password=facebook_id,
            auth_provider=auth_provider,
            is_active=is_active,
        )

        return user

    @staticmethod
    def login_facebook_user(user, facebook_id):
        login_uri = reverse_lazy("login_api_view")
        domain = settings.BASE_BACKEND_URL
        redirect_uri = f"{domain}{login_uri}"

        data = {
            "email": user.email,
            "password": facebook_id,
        }

        response = requests.post(redirect_uri, data=data)

        if response.status_code != 200:
            return Response(response.json(), status=response.status_code)

        return response.json()
