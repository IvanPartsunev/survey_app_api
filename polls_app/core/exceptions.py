from django.db import IntegrityError
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, IntegrityError):
        response.data = {"error": "Resource not found or integrity constraint violated"}
        response.status_code = 400

    return response