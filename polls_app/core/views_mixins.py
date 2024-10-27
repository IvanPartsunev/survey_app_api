from rest_framework import status
from rest_framework.response import Response

from polls_app.core.services import check_ownership_service, remove_comment_from_token_service


class UpdateDeleteMixin:

    def patch(self, request, *args, **kwargs):
        """
        PATCH request to edit an object with the given ID.
        """
        instance = self.get_object()

        # Check ownership for authenticated and anonymous users
        if not check_ownership_service(request, instance):
            return Response(
                {"detail": "You do not have permission to edit this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(
            {"message": "Resource successfully updated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """
        DELETE request to delete an object with the given ID.
        """
        instance = self.get_object()

        # Check ownership for authenticated and anonymous users
        if not check_ownership_service(request, instance):
            return Response(
                {"detail": "You do not have permission to delete this comment."},
                status=status.HTTP_403_FORBIDDEN,
            )

        response = Response(
                {"message": "Successfully deleted"},
                status=status.HTTP_204_NO_CONTENT,
            )

        if not request.user.is_authenticated:
            token = remove_comment_from_token_service(request, instance.id)
            response.set_cookie("anonymous_user_token", token, httponly=True, max_age=60 * 60 * 24)  # 1 day expiration

        instance.delete()

        return response



