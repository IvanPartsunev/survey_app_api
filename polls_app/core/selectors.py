from polls_app.core.models import ProductModel, QuestionModel, AnswerModel, CommentModel


class ProductsSelector:
    def __init__(self, user):
        self.user = user

    def get_queryset(self):
        return ProductModel.objects.filter(owner=self.user)


class QuestionSelector:
    def __init__(self, user, product):
        self.user = user
        self.product = product

    def get_queryset(self):
        return QuestionModel.objects.filter(owner=self.user, product=self.product)


class AnswerSelector:
    def __init__(self, question_id):
        self.question = question_id

    def get_queryset(self):
        return AnswerModel.objects.filter(question=self.question)


class CommentSelector:
    def __init__(self, question_id):
        self.question = question_id

    def get_queryset(self):
        return CommentModel.objects.filter(question=self.question)
