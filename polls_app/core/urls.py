from django.urls import path

from polls_app.core.views import ProductsListCreateApiView, ProductRetrieveUpdateDeleteApiView, \
    QuestionRetrieveUpdateDeleteApiView, QuestionCreateApiView, \
    AnswersCreateApiView, AnswersUpdateDeleteApiView, CommentsCreateApiView, CommentsUpdateDeleteApiView, \
    AnswerVoteApiView

urlpatterns = (
    path("products/", ProductsListCreateApiView.as_view(), name="products"),
    path("products/<int:pk>/", ProductRetrieveUpdateDeleteApiView.as_view(), name="product"),
    path("questions/", QuestionCreateApiView.as_view(), name="question"),
    path("questions/<int:pk>/", QuestionRetrieveUpdateDeleteApiView.as_view(), name="question"),
    path("answers/", AnswersCreateApiView.as_view(), name="answer"),
    path("answers/<int:pk>/", AnswersUpdateDeleteApiView.as_view(), name="answers"),
    path("answers/<int:pk>/vote", AnswerVoteApiView.as_view(), name="answers"),
    path("comments/", CommentsCreateApiView.as_view(), name="comment"),
    path("comments/<int:pk>/", CommentsUpdateDeleteApiView.as_view(), name="comments"),
)
