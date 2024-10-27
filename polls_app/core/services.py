import uuid
import jwt

from datetime import timedelta

from django.utils import timezone
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from rest_framework.response import Response

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


def generate_comment_jwt_token_service(comment_id, question_id, token):
    if token is None:
        guest_id = str(uuid.uuid4())
        payload = {
            "guest_id": guest_id,
            "questions": {question_id: comment_id},
            "exp": timezone.now() + timedelta(hours=24),
        }
    else:
        payload = decode_comment_jwt_token_service(token)
        payload["questions"][question_id] = comment_id

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_comment_jwt_token_service(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload

    except jwt.ExpiredSignatureError:
        raise jwt.ExpiredSignatureError("Token has expired")

    except jwt.InvalidTokenError:
        raise jwt.InvalidTokenError("Invalid token")


def validate_comment_uniqueness_service(question_id, token):
    # If there’s no token, assume no prior comment
    if token is None:
        return

    # Decode the existing token
    payload = decode_comment_jwt_token_service(token)

    # Check if a comment for this question already exists in the payload
    if str(question_id) in payload["questions"]:
        raise ValueError(f"Question ID {question_id} already has a comment from this user.")


def check_ownership_service(request, instance):
    """
    Verifies whether the current user or anonymous guest owns the object.
    """
    user = request.user

    if user.is_authenticated:
        return instance.owner == user.username or instance.owner == user  # If authenticated, check if the user is the owner of the comment

    # If anonymous, validate ownership using the token
    token = request.COOKIES.get("anonymous_user_token")
    if not token:
        return False

    try:
        payload = decode_comment_jwt_token_service(token)
        if instance.id not in payload["questions"].values():
            return False
        return True

    except jwt.InvalidTokenError:
        return False

def remove_comment_from_token_service(request, comment_id):
    token = request.COOKIES.get("anonymous_user_token")
    payload = decode_comment_jwt_token_service(token)

    payload["questions"] = {k: v for k, v in payload["questions"].items() if v != comment_id}

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


def vote_on_answer_service(request, answer):
    # Get the voted answers from cookies (defaults to an empty list if none)
    voted_answers = request.COOKIES.get("voted_answers", "").split(",")

    # Check if the user has already voted on this answer
    if str(answer.id) in voted_answers:
        return Response({"detail": "You have already voted on this answer."}, status=400)

    answer.votes += 1
    answer.save()

    # Update the cookie with the new answer ID
    voted_answers.append(str(answer.id))
    response = Response({"message": "Your vote has been counted."}, status=200)
    response.set_cookie("voted_answers", ",".join(voted_answers), httponly=True, max_age=60 * 60 * 24 * 30)  # 30 days

    return response