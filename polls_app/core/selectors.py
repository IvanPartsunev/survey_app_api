from oauthlib.uri_validate import query

from polls_app.core.models import ProductModel, QuestionModel, AnswerModel, CommentModel


class ProductsSelector:
    def __init__(self, user):
        self.user = user

    def get_queryset(self):
        queryset = (ProductModel.objects.filter(owner=self.user)
                    .prefetch_related("questions", "questions__question_answers", "questions__question_comments"))
        return queryset


class QuestionSelector:
    def __init__(self, user, question_id, method):
        self.user = user
        self.question_id = question_id
        self.method = method

    def get_queryset(self):
        if self.method.lower() == "get":
            queryset = (QuestionModel.objects.filter(owner=self.user, id=self.question_id)
                        .select_related("owner")
                        .prefetch_related("question_answers", "question_comments"))
            return queryset

        queryset = QuestionModel.objects.filter(owner=self.user, id=self.question_id)
        return queryset

