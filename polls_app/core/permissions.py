from rest_framework import exceptions


class IsOwner:

    @staticmethod
    def product_permission_check(product, user):
        if product.owner != user:
            raise exceptions.PermissionDenied()

    @staticmethod
    def question_permission_check(question, user):
        if question.owner != user:
            raise exceptions.PermissionDenied()


