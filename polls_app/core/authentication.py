import jwt

from django.contrib.auth.models import AnonymousUser

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from drf_spectacular.extensions import OpenApiAuthenticationExtension

from polls_app.core.services import decode_comment_jwt_token_service


class AnonymousUserJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.COOKIES.get('anonymous_user_token', None)

        if not token:
            return None  # No token found, return None to allow other authentication methods

        try:
            payload = decode_comment_jwt_token_service(token)
            guest_id = payload.get('guest_id')

            if not guest_id:
                raise AuthenticationFailed('Invalid token: guest ID missing')

            user = AnonymousUser()
            user.guest_id = guest_id  # Assign the guest ID to the user object

            return user, token

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')

        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')


class AnonymousUserJWTAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = 'polls_app.core.authentication.AnonymousUserJWTAuthentication'  # The full path to your auth class
    name = 'AnonymousUserJWTAuthentication'  # The name used in the OpenAPI schema

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'cookie',
            'name': 'anonymous_user_token',  # This refers to the cookie name where the token is stored
            'description': 'JWT token for anonymous user comments',
        }