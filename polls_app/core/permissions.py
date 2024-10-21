from rest_framework import exceptions
from rest_framework.permissions import BasePermission


def is_owner(obj, user):
    if obj.owner != user:
        raise exceptions.PermissionDenied()


class IsAuthenticatedOrJWTGuest(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_authenticated or hasattr(request.user, 'guest_id')))