from django.http import Http404
from django.contrib.contenttypes.models import ContentType

from polls_app.core.permissions import is_owner
from polls_app.custom_exeption import ApplicationError


def get_object_and_check_permission_service(app_label, model_name, obj_id, user):
    try:
        content_type = ContentType.objects.get(app_label=app_label, model=model_name.lower())
    except ContentType.DoesNotExist:
        raise ApplicationError(f"Content type for '{model_name}' in app '{app_label}' not found.")

    model_class = content_type.model_class()

    try:
        current_object = model_class.objects.get(id=obj_id)
    except model_class.DoesNotExist:
        raise Http404(f"Object of {model_class.__name__} with the given ID does not exists.")

    if user:
        is_owner(current_object, user)

    return current_object