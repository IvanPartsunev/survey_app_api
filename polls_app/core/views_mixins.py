from rest_framework import status
from rest_framework.response import Response

from polls_app.core.services import get_object_and_check_permission_service


class UpdateDeleteMixin:

    def patch(self, request, *args, **kwargs):
        """
        PATCH request edit an object with the given id.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(
            {"message": "Resource successfully updated", "data": serializer.data},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, *args, **kwargs):
        """
        DELETE request delete and object with the given id.
        """
        instance = self.get_object()
        instance.delete()

        return Response(
            {"message": "Successfully deleted"},
            status=status.HTTP_204_NO_CONTENT,
        )


class AnswersCommentsPostMixin:

    def post(self, request, *args, **kwargs):
        """
        POST request CREATE an object for the question.
        """

        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question_id = serializer.initial_data.get("question_id")

        question = get_object_and_check_permission_service("core", "questionmodel", question_id, None)

        serializer.save(question=question, owner=user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
