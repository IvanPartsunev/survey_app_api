from rest_framework import exceptions


def is_owner(obj, user):
    if obj.owner != user:
        raise exceptions.PermissionDenied()


