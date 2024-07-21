from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit, view or delete it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.owner_id == request.user.id

