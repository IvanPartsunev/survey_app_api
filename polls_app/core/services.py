import jwt

from datetime import timedelta

from django.utils import timezone
from django.http import Http404
from django.contrib.contenttypes.models import ContentType

from polls_app.core.permissions import is_owner
from polls_app.custom_exeption import ApplicationError
from polls_app.settings import SECRET_KEY


def get_object_and_check_permission_service(app_label, model_name, obj_id, user):
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name.lower())
    except ContentType.DoesNotExist:
        raise ApplicationError(f"Content type for '{model_name}' in app '{app_label}' not found.")

    model_class = content_type.model_class()

    try:
        current_object = model_class.objects.get(id=obj_id)
    except model_class.DoesNotExist:
        raise Http404(f"{model_class.class_name()} with the given ID does not exists.")

    if user:
        is_owner(current_object, user)

    return current_object


def generate_comment_jwt_token_service(guest_id):
    payload = {
        "guest_id": guest_id,
        "exp": timezone.now() + timedelta(hours=24),
        "scope": "comment",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_comment_jwt_token_service(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("scope") != "comment":
            raise jwt.InvalidTokenError("Invalid scope for token")
        return payload
    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")
    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")
